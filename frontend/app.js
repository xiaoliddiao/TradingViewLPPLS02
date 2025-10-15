// Trading Data Aggregator - Frontend Application

class TradingApp {
    constructor() {
        this.chart = null;
        this.candlestickSeries = null;
        this.lineSeries = null;
        this.areaSeries = null;
        this.barSeries = null;
        this.currentSeries = null;
        this.currentData = {};
        this.currentSymbol = 'BTC';
        
        this.init();
    }
    
    init() {
        // Initialize event listeners
        document.getElementById('fetchButton').addEventListener('click', () => this.fetchData());
        document.getElementById('symbolInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.fetchData();
        });
        document.getElementById('chartType').addEventListener('change', (e) => this.changeChartType(e.target.value));
        document.getElementById('dataSource').addEventListener('change', (e) => this.changeDataSource(e.target.value));
        
        // Initialize chart
        this.initChart();
        
        // Fetch default data (BTC)
        this.fetchData();
    }
    
    initChart() {
        const container = document.getElementById('chartContainer');
        
        // Create chart with TradingView Lightweight Charts
        this.chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: 600,
            layout: {
                background: { color: '#161B22' },
                textColor: '#E6EDF3',
            },
            grid: {
                vertLines: { color: '#30363D' },
                horzLines: { color: '#30363D' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#30363D',
            },
            timeScale: {
                borderColor: '#30363D',
                timeVisible: true,
                secondsVisible: false,
            },
        });
        
        // Add candlestick series by default
        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#26A69A',
            downColor: '#EF5350',
            borderVisible: false,
            wickUpColor: '#26A69A',
            wickDownColor: '#EF5350',
        });
        
        this.currentSeries = this.candlestickSeries;
        
        // Handle window resize
        window.addEventListener('resize', () => {
            this.chart.applyOptions({ width: container.clientWidth });
        });
    }
    
    async fetchData() {
        const symbol = document.getElementById('symbolInput').value.trim() || 'BTC';
        const days = parseInt(document.getElementById('daysInput').value) || 90;
        const button = document.getElementById('fetchButton');
        
        // Disable button and show loading
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span> Fetching...';
        
        // Clear previous data
        this.currentData = {};
        this.updateAdaptersStatus([]);
        
        try {
            const response = await fetch('/api/fetch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symbol, days }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.currentSymbol = symbol;
            
            // Update adapters status
            this.updateAdaptersStatus(data.results);
            
            // Store successful data
            data.results.forEach(result => {
                if (result.success && result.data && result.data.length > 0) {
                    this.currentData[result.adapter_name] = result.data;
                }
            });
            
            // Update data source dropdown
            this.updateDataSourceDropdown();
            
            // Display first successful data source
            const firstSuccessful = Object.keys(this.currentData)[0];
            if (firstSuccessful) {
                this.displayChartData(firstSuccessful);
            } else {
                this.updateChartInfo('No data available from any source. Please check adapter status above.');
            }
            
        } catch (error) {
            console.error('Error fetching data:', error);
            this.updateChartInfo(`Error: ${error.message}`);
        } finally {
            button.disabled = false;
            button.textContent = 'Fetch Data';
        }
    }
    
    updateAdaptersStatus(results) {
        const container = document.getElementById('adaptersStatus');
        
        if (results.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">Loading...</p>';
            return;
        }
        
        container.innerHTML = results.map(result => {
            const statusIcon = result.success ? '✓' : '✗';
            const statusClass = result.success ? 'status-success' : 'status-error';
            const dataCount = result.data ? result.data.length : 0;
            
            return `
                <div class="adapter-card">
                    <div class="adapter-header">
                        <span class="adapter-name">${result.adapter_name}</span>
                        <span class="adapter-status ${statusClass}">${statusIcon}</span>
                    </div>
                    ${result.success ? `
                        <div class="adapter-info">
                            ✓ ${dataCount} data points retrieved<br>
                            ${result.rate_limit_info || ''}
                        </div>
                    ` : `
                        <div class="adapter-error">
                            ${result.error || 'Unknown error'}
                        </div>
                        ${result.rate_limit_info ? `
                            <div class="adapter-info">${result.rate_limit_info}</div>
                        ` : ''}
                    `}
                </div>
            `;
        }).join('');
    }
    
    updateDataSourceDropdown() {
        const select = document.getElementById('dataSource');
        const sources = Object.keys(this.currentData);
        
        select.innerHTML = sources.map(source => 
            `<option value="${source}">${source}</option>`
        ).join('');
        
        if (sources.length > 0) {
            select.value = sources[0];
        }
    }
    
    changeDataSource(source) {
        if (this.currentData[source]) {
            this.displayChartData(source);
        }
    }
    
    displayChartData(sourceName) {
        const data = this.currentData[sourceName];
        if (!data || data.length === 0) return;
        
        // Convert data to TradingView format
        const chartData = data.map(bar => ({
            time: bar.time,
            open: bar.open,
            high: bar.high,
            low: bar.low,
            close: bar.close,
            value: bar.close, // For line/area charts
        }));
        
        // Update current series
        this.currentSeries.setData(chartData);
        
        // Fit content
        this.chart.timeScale().fitContent();
        
        // Update info
        this.updateChartInfo(
            `Displaying ${data.length} bars from <strong>${sourceName}</strong> for symbol <strong>${this.currentSymbol}</strong>`
        );
    }
    
    changeChartType(type) {
        if (!this.currentSeries) return;
        
        // Get current data
        const currentSource = document.getElementById('dataSource').value;
        const data = this.currentData[currentSource];
        if (!data) return;
        
        // Remove current series
        this.chart.removeSeries(this.currentSeries);
        
        // Create new series based on type
        switch (type) {
            case 'candlestick':
                this.currentSeries = this.chart.addCandlestickSeries({
                    upColor: '#26A69A',
                    downColor: '#EF5350',
                    borderVisible: false,
                    wickUpColor: '#26A69A',
                    wickDownColor: '#EF5350',
                });
                break;
            
            case 'line':
                this.currentSeries = this.chart.addLineSeries({
                    color: '#2962FF',
                    lineWidth: 2,
                });
                break;
            
            case 'area':
                this.currentSeries = this.chart.addAreaSeries({
                    topColor: 'rgba(41, 98, 255, 0.4)',
                    bottomColor: 'rgba(41, 98, 255, 0.0)',
                    lineColor: '#2962FF',
                    lineWidth: 2,
                });
                break;
            
            case 'bar':
                this.currentSeries = this.chart.addBarSeries({
                    upColor: '#26A69A',
                    downColor: '#EF5350',
                });
                break;
        }
        
        // Redisplay data
        this.displayChartData(currentSource);
    }
    
    updateChartInfo(message) {
        document.getElementById('chartInfo').innerHTML = message;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new TradingApp();
});
