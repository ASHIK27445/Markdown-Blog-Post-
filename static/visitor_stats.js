// Visitor Statistics Charts and Graphs
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts
    initDailyVisitsChart();
    initBlogPopularityChart();
    initVisitorMetricsChart();
    initVisitTrendsChart();
    
    // Add refresh functionality
    initRefreshButton();
});

function initDailyVisitsChart() {
    const ctx = document.getElementById('dailyVisitsChart');
    if (!ctx) return;

    const chartData = parseDailyVisitsData();
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Daily Visits',
                data: chartData.visits,
                backgroundColor: 'rgba(139, 92, 246, 0.7)',
                borderColor: 'rgba(139, 92, 246, 1)',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Daily Visits Overview',
                    color: '#ffffff',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#8b5cf6',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

function initBlogPopularityChart() {
    const ctx = document.getElementById('blogPopularityChart');
    if (!ctx) return;

    const chartData = parseBlogPopularityData();
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.visits,
                backgroundColor: [
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(139, 92, 246, 0.6)',
                    'rgba(236, 72, 153, 0.6)',
                    'rgba(59, 130, 246, 0.6)',
                    'rgba(16, 185, 129, 0.6)'
                ],
                borderColor: [
                    'rgba(139, 92, 246, 1)',
                    'rgba(236, 72, 153, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(236, 72, 153, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 2,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#ffffff',
                        font: {
                            size: 12
                        },
                        padding: 20
                    }
                },
                title: {
                    display: true,
                    text: 'Blog Popularity Distribution',
                    color: '#ffffff',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${value} visits (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function initVisitorMetricsChart() {
    const ctx = document.getElementById('visitorMetricsChart');
    if (!ctx) return;

    const metricsData = parseVisitorMetricsData();
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Total Visits', 'Unique Visitors', 'Today\'s Visits', 'Today\'s Unique', 'Engagement'],
            datasets: [{
                label: 'Visitor Metrics',
                data: [
                    metricsData.totalVisits,
                    metricsData.uniqueVisitors,
                    metricsData.todayVisits,
                    metricsData.todayUnique,
                    metricsData.engagement
                ],
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                borderColor: 'rgba(139, 92, 246, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(139, 92, 246, 1)',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#ffffff',
                        font: {
                            size: 12
                        }
                    },
                    ticks: {
                        color: '#ffffff',
                        backdropColor: 'transparent'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Visitor Metrics Overview',
                    color: '#ffffff',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            }
        }
    });
}

function initVisitTrendsChart() {
    const ctx = document.getElementById('visitTrendsChart');
    if (!ctx) return;

    const trendData = parseVisitTrendsData();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.labels,
            datasets: [{
                label: 'Total Visits',
                data: trendData.totalVisits,
                borderColor: 'rgba(139, 92, 246, 1)',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: 'rgba(139, 92, 246, 1)',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4
            }, {
                label: 'Unique Visitors',
                data: trendData.uniqueVisitors,
                borderColor: 'rgba(236, 72, 153, 1)',
                backgroundColor: 'rgba(236, 72, 153, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: 'rgba(236, 72, 153, 1)',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Visit Trends Over Time',
                    color: '#ffffff',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    labels: {
                        color: '#ffffff'
                    }
                }
            },
            scales: {
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

// Data parsing functions
function parseDailyVisitsData() {
    const dailyItems = document.querySelectorAll('.daily-stat-item');
    const labels = [];
    const visits = [];

    dailyItems.forEach(item => {
        const date = item.querySelector('.date').textContent;
        const visitCount = parseInt(item.querySelector('.visit-count').textContent);
        
        labels.push(date);
        visits.push(visitCount);
    });

    return { labels: labels.reverse(), visits: visits.reverse() };
}

function parseBlogPopularityData() {
    const blogItems = document.querySelectorAll('.popular-blog-item');
    const labels = [];
    const visits = [];

    blogItems.forEach(item => {
        const title = item.querySelector('h4').textContent;
        const visitCount = parseInt(item.querySelector('.count').textContent);
        
        labels.push(title.length > 20 ? title.substring(0, 20) + '...' : title);
        visits.push(visitCount);
    });

    return { labels, visits };
}

function parseVisitorMetricsData() {
    const statCards = document.querySelectorAll('.stat-card');
    const metrics = {
        totalVisits: parseInt(statCards[0].querySelector('.stat-number').textContent),
        uniqueVisitors: parseInt(statCards[1].querySelector('.stat-number').textContent),
        todayVisits: parseInt(statCards[2].querySelector('.stat-number').textContent),
        todayUnique: parseInt(statCards[3].querySelector('.stat-number').textContent),
        engagement: 0
    };

    // Calculate engagement score (simplified)
    metrics.engagement = Math.min(100, Math.round(
        (metrics.todayUnique / Math.max(1, metrics.uniqueVisitors)) * 100
    ));

    return metrics;
}

function parseVisitTrendsData() {
    const dailyItems = document.querySelectorAll('.daily-stat-item');
    const labels = [];
    const totalVisits = [];
    const uniqueVisitors = [];

    dailyItems.forEach(item => {
        const date = item.querySelector('.date').textContent;
        const visitCount = parseInt(item.querySelector('.visit-count').textContent);
        
        labels.push(date);
        totalVisits.push(visitCount);
        // For demo purposes, unique visitors is estimated
        uniqueVisitors.push(Math.max(1, Math.round(visitCount * 0.7)));
    });

    return {
        labels: labels.reverse(),
        totalVisits: totalVisits.reverse(),
        uniqueVisitors: uniqueVisitors.reverse()
    };
}

function initRefreshButton() {
    const refreshBtn = document.getElementById('refreshStats');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.classList.add('refreshing');
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
            
            setTimeout(() => {
                location.reload();
            }, 1000);
        });
    }
}

// Export functions for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initDailyVisitsChart,
        initBlogPopularityChart,
        initVisitorMetricsChart,
        initVisitTrendsChart
    };
}