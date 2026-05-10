# Design Document: InsightFlow Dashboard Enhancements

## Overview

The InsightFlow dashboard is a Streamlit-based analytics platform for e-commerce product data. The current implementation provides basic functionality with 5 tabs: Product List, Price Analysis, Compare Selected, Data Details, and System Health. This enhancement project adds 15 advanced features to transform the dashboard into a comprehensive analytics tool for price tracking, product analysis, and system monitoring.

### Key Design Goals
1. **Enhanced User Experience**: Improve navigation, organization, and accessibility
2. **Advanced Analytics**: Add historical tracking, categorization, and multi-platform comparison
3. **Data Quality & Reliability**: Implement data quality indicators and persistence
4. **Performance & Scalability**: Support real-time updates and handle larger datasets
5. **Extensibility**: Design modular architecture for future feature additions

### Scope
This design covers 15 new features across four main categories:
- **Data Analysis**: Historical price tracking, categorization, filtering, search
- **User Features**: Price alerts, preferences, export, navigation
- **System Features**: Performance metrics, data quality, persistence, real-time updates
- **Accessibility**: WCAG compliance, internationalization

## Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    InsightFlow Dashboard                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer (Streamlit)                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   UI Tabs   │ │ Components  │ │  Widgets    │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Data Models │ │  Services   │ │  Utilities  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  Data Access Layer                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Parquet    │ │   JSON      │ │ Local Storage│          │
│  │   Files     │ │   Cache     │ │   (Browser)  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  External Services                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │  Crawlers   │ │ Notification│ │  Analytics  │           │
│  │             │ │   Services  │ │   Tools     │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. Frontend Layer (Streamlit)
- **Tab Manager**: Manages tab organization and navigation
- **Component Library**: Reusable UI components (charts, filters, tables)
- **State Manager**: Handles session state and user preferences
- **Theme Manager**: Manages visual themes and accessibility settings

#### 2. Business Logic Layer
- **Data Transformation Service**: Handles data filtering, sorting, aggregation
- **Analytics Engine**: Calculates metrics, trends, and statistical measures
- **Alert Engine**: Monitors price conditions and triggers notifications
- **Categorization Service**: Manages product grouping and classification
- **Export Service**: Handles data export in multiple formats

#### 3. Data Access Layer
- **Parquet Data Store**: Primary storage for product data
- **Historical Data Store**: Time-series data for price tracking
- **User Preferences Store**: Browser local storage for user settings
- **Alert Configuration Store**: Persistent storage for alert rules
- **Category Definition Store**: Storage for product categories

#### 4. External Integration Layer
- **Crawler Interface**: Communicates with data collection crawlers
- **Notification Service**: Integrates with email/Telegram for alerts
- **Analytics Integration**: Optional integration with external analytics tools

### Data Flow

```
1. User Interaction → Tab Manager → Component Library
2. Component Events → State Manager → Business Logic
3. Business Logic → Data Access Layer → Parquet/JSON Files
4. Data Processing → Analytics Engine → Visualization Components
5. Alert Conditions → Alert Engine → Notification Service
```

## Components and Interfaces

### Core Components

#### 1. Historical Price Tracker
- **Purpose**: Track and visualize price changes over time
- **Inputs**: Product selection, time range, comparison settings
- **Outputs**: Line charts, metrics, trend analysis
- **Dependencies**: Historical data store, visualization library

#### 2. Price Alert System
- **Purpose**: Monitor prices and trigger notifications
- **Inputs**: Alert conditions (thresholds, percentages), notification preferences
- **Outputs**: Dashboard notifications, external alerts (email/Telegram)
- **Dependencies**: Alert configuration store, notification service

#### 3. Product Categorization Engine
- **Purpose**: Group products into meaningful categories
- **Inputs**: Product attributes, manual assignments, keyword patterns
- **Outputs**: Category assignments, suggested categories
- **Dependencies**: Category definition store, keyword matching algorithm

#### 4. Advanced Filter System
- **Purpose**: Filter products by multiple criteria
- **Inputs**: Filter conditions (price, platform, date, category, quality)
- **Outputs**: Filtered product lists, filter state persistence
- **Dependencies**: Data transformation service, state manager

#### 5. Export Service
- **Purpose**: Export data in various formats
- **Inputs**: Data selection, format preferences, export settings
- **Outputs**: CSV, Excel, PDF, JSON files
- **Dependencies**: Data transformation, file generation libraries

#### 6. Performance Metrics Dashboard
- **Purpose**: Monitor system performance and health
- **Inputs**: System metrics, crawler logs, resource usage
- **Outputs**: Performance charts, warning indicators, detailed logs
- **Dependencies**: System monitoring, log aggregation

#### 7. Visualization Library
- **Purpose**: Provide diverse chart types for data analysis
- **Inputs**: Data sets, visualization preferences, chart parameters
- **Outputs**: Line charts, bar charts, scatter plots, heatmaps, etc.
- **Dependencies**: Streamlit charting, Plotly/Altair integration

#### 8. User Preferences Manager
- **Purpose**: Manage user settings and preferences
- **Inputs**: User configuration changes, default settings
- **Outputs**: Persistent preferences, theme application
- **Dependencies**: Local storage, theme manager

#### 9. Multi-Platform Comparator
- **Purpose**: Compare products across different e-commerce platforms
- **Inputs**: Products from multiple platforms, comparison criteria
- **Outputs**: Unified comparison views, cross-platform metrics
- **Dependencies**: Data normalization, platform mapping

#### 10. Data Quality Assessor
- **Purpose**: Assess and display data quality indicators
- **Inputs**: Product data, quality metrics, freshness information
- **Outputs**: Quality scores, warning indicators, summary dashboards
- **Dependencies**: Data validation rules, anomaly detection

#### 11. Navigation Manager
- **Purpose**: Organize and manage dashboard navigation
- **Inputs**: Tab definitions, user preferences, screen size
- **Outputs**: Tab organization, navigation controls, shortcuts
- **Dependencies**: Tab manager, responsive design

#### 12. Session Persistence Manager
- **Purpose**: Preserve user work across sessions
- **Inputs**: User state, selections, filters, preferences
- **Outputs**: Auto-saved state, session restoration options
- **Dependencies**: Browser local storage, state serialization

#### 13. Accessibility Manager
- **Purpose**: Ensure WCAG compliance and internationalization
- **Inputs**: Accessibility settings, language preferences, locale
- **Outputs**: Accessible UI components, localized content, RTL support
- **Dependencies**: Translation files, accessibility libraries

#### 14. Real-time Update Manager
- **Purpose**: Handle real-time data updates and notifications
- **Inputs**: Crawler progress, new data availability, user preferences
- **Outputs**: Progress indicators, auto-refresh, update notifications
- **Dependencies**: WebSocket/SSE, data change detection

#### 15. Advanced Search Engine
- **Purpose**: Provide sophisticated search capabilities
- **Inputs**: Search queries, search history, saved searches
- **Outputs**: Search results, relevance ranking, suggestions
- **Dependencies**: Fuzzy matching, semantic search algorithms

### Interface Definitions

#### Data Models Interface
```python
class ProductData:
    id: str
    title: str
    price: float
    url: str
    source_platform: str
    timestamp: datetime
    category: Optional[str]
    data_quality_score: float
    historical_prices: List[PricePoint]
    
class PricePoint:
    timestamp: datetime
    price: float
    source: str
    
class AlertRule:
    id: str
    product_id: str
    condition_type: str  # "threshold", "percentage", "time_window"
    condition_value: float
    notification_method: str  # "dashboard", "email", "telegram"
    is_active: bool
    
class UserPreferences:
    theme: str
    default_view: str
    refresh_interval: int
    export_format: str
    language: str
    accessibility_settings: Dict[str, Any]
```

#### Service Interfaces
```python
class HistoricalPriceService:
    def get_price_history(product_id: str, time_range: str) -> List[PricePoint]
    def calculate_metrics(price_history: List[PricePoint]) -> Dict[str, float]
    def compare_trends(product_ids: List[str]) -> ComparisonResult
    
class AlertService:
    def create_alert(rule: AlertRule) -> str
    def check_alerts(product_data: ProductData) -> List[AlertTrigger]
    def send_notification(trigger: AlertTrigger) -> bool
    
class CategorizationService:
    def assign_category(product: ProductData, category: str) -> bool
    def suggest_categories(product: ProductData) -> List[str]
    def get_products_by_category(category: str) -> List[ProductData]
    
class ExportService:
    def export_csv(data: pd.DataFrame, options: ExportOptions) -> bytes
    def export_excel(data: pd.DataFrame, options: ExportOptions) -> bytes
    def export_pdf(data: pd.DataFrame, options: ExportOptions) -> bytes
    def export_json(data: pd.DataFrame, options: ExportOptions) -> bytes
```

## Data Models

### Core Data Models

#### 1. Product Data Model
```python
{
    "id": "unique_product_identifier",
    "title": "Product Name",
    "price": 999000.0,
    "display_price": "999.000đ",
    "url": "https://example.com/product",
    "source_platform": "Shopee",
    "timestamp": "2024-01-15T10:30:00Z",
    "category": "Electronics",
    "data_quality": {
        "completeness_score": 0.95,
        "freshness_score": 0.98,
        "accuracy_score": 0.92,
        "overall_score": 0.95
    },
    "metadata": {
        "specs": {...},
        "images": [...],
        "seller_info": {...}
    }
}
```

#### 2. Historical Price Data Model
```python
{
    "product_id": "unique_product_identifier",
    "price_history": [
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "price": 1000000.0,
            "source": "crawl_001"
        },
        {
            "timestamp": "2024-01-02T10:00:00Z",
            "price": 950000.0,
            "source": "crawl_002"
        }
    ],
    "metrics": {
        "volatility": 0.05,
        "average_price": 975000.0,
        "max_price": 1000000.0,
        "min_price": 950000.0,
        "trend": "decreasing"
    }
}
```

#### 3. Alert Configuration Model
```python
{
    "alert_id": "alert_001",
    "user_id": "user_001",
    "product_id": "product_001",
    "condition": {
        "type": "price_threshold",
        "operator": "<",
        "value": 800000.0
    },
    "notification": {
        "method": ["dashboard", "email"],
        "email_address": "user@example.com",
        "telegram_chat_id": "123456789"
    },
    "status": "active",
    "created_at": "2024-01-15T10:00:00Z",
    "last_triggered": null
}
```

#### 4. Category Definition Model
```python
{
    "category_id": "electronics",
    "name": "Electronics",
    "description": "Electronic devices and accessories",
    "rules": [
        {
            "field": "title",
            "pattern": "phone|smartphone|mobile",
            "type": "keyword"
        },
        {
            "field": "title",
            "pattern": "laptop|notebook|ultrabook",
            "type": "keyword"
        }
    ],
    "products": ["product_001", "product_002"],
    "created_by": "user_001",
    "created_at": "2024-01-15T10:00:00Z"
}
```

#### 5. User Preferences Model
```python
{
    "user_id": "user_001",
    "display": {
        "theme": "dark",
        "density": "compact",
        "font_size": "medium",
        "color_blind_mode": false
    },
    "behavior": {
        "auto_refresh": true,
        "refresh_interval": 300,
        "default_tab": "product_list",
        "remember_filters": true
    },
    "export": {
        "default_format": "csv",
        "include_metadata": true,
        "timestamp_format": "iso"
    },
    "notifications": {
        "enable_dashboard_alerts": true,
        "enable_email_alerts": false,
        "enable_telegram_alerts": true
    },
    "accessibility": {
        "keyboard_navigation": true,
        "screen_reader_support": true,
        "high_contrast": false,
        "reduced_motion": false
    }
}
```

### Database Schema

#### Parquet File Structure
```
data/history/
├── products_shopee_20240115.parquet
├── products_shopee_20240116.parquet
├── products_tgdd_20240115.parquet
└── historical/
    ├── price_history_202401.parquet
    └── alert_history_202401.parquet
```

#### Local Storage Structure
```json
{
    "user_preferences": {...},
    "session_state": {
        "current_filters": {...},
        "selected_products": [...],
        "active_tab": "product_list",
        "search_history": [...]
    },
    "alert_configurations": [...],
    "category_definitions": [...],
    "saved_searches": [...]
}
```

### Data Relationships
```
Product ──┐
          ├── HistoricalPrice (one-to-many)
          ├── AlertRule (one-to-many)
          └── Category (many-to-many)
          
User ─────┐
          ├── UserPreferences (one-to-one)
          ├── AlertRule (one-to-many)
          └── SavedSearch (one-to-many)
          
Platform ─┐
          └── Product (one-to-many)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

**PBT Applicability Assessment**: This feature involves data transformations, filtering logic, calculations, and business rules that are suitable for property-based testing. The UI rendering and Streamlit components are not suitable for PBT, but the core business logic (data processing, calculations, transformations) is appropriate.

Now I need to use the prework tool to analyze the acceptance criteria before writing the correctness properties section.

### UI/UX Design

#### 1. Navigation Redesign

**Current Issue**: 5 tabs in horizontal layout, limited organization
**Solution**: Hierarchical navigation with sidebar groups

```
SIDEBAR NAVIGATION
├── 📊 Data Views
│   ├── Product List
│   ├── Price Analysis
│   └── Data Details
├── 🔍 Analysis Tools
│   ├── Compare Selected
│   ├── Historical Trends
│   ├── Category Analysis
│   └── Platform Comparison
├── ⚙️ Management
│   ├── Alert Configuration
│   ├── User Preferences
│   └── Export Manager
├── 📈 Monitoring
│   ├── Data Quality Dashboard
│   ├── Performance Metrics
│   └── System Health
└── 🔎 Search & Filter
    ├── Advanced Search
    └── Saved Filters
```

#### 2. Enhanced Product List View

**Components**:
- **Search Bar**: Fuzzy search with auto-completion
- **Quick Filters**: Price range, platform, category chips
- **Data Quality Indicators**: Color-coded badges for completeness
- **Bulk Actions**: Select multiple products for comparison/categorization
- **View Toggle**: Grid vs list view options

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ [Search...] [🔍]  [Price: ▾] [Platform: ▾] [Category: ▾]    │
├─────────────────────────────────────────────────────────────┤
│ Product 1 │ ⭐ 95% │ $100 │ Shopee │ Electronics ▾ │ ⚡     │
│ Product 2 │ ⭐ 87% │ $150 │ TGDD   │ Phones     ▾ │ ⚡     │
│ Product 3 │ ⭐ 92% │ $200 │ Cellph.│ Accessories▾ │ ⚡     │
└─────────────────────────────────────────────────────────────┘
```

#### 3. Historical Price Chart View

**Components**:
- **Time Range Selector**: Day/Week/Month/Custom with calendar
- **Chart Type Selector**: Line/Area/Bar/Candlestick
- **Comparison Mode**: Overlay multiple products, show difference
- **Metrics Panel**: Volatility, average, min/max, trend indicators
- **Export Controls**: Save chart as image, export data

**Visual Design**:
- Interactive tooltips on hover
- Zoom and pan capabilities
- Multiple Y-axes for different scales
- Annotations for significant events

#### 4. Alert Configuration Interface

**Components**:
- **Product Selector**: Search and select products
- **Condition Builder**: Visual rule builder with dropdowns
- **Notification Settings**: Channel selection, frequency limits
- **Test Button**: Simulate alert with current data
- **History View**: Past triggered alerts with details

#### 5. Data Quality Dashboard

**Components**:
- **Score Cards**: Overall quality, completeness, freshness, accuracy
- **Trend Charts**: Quality metrics over time
- **Issue List**: Products with quality problems
- **Drill-down**: Click scores to see affected products
- **Improvement Suggestions**: Automated recommendations

### Technical Implementation Details

#### 1. Streamlit Enhancements

**Session State Management**:
```python
class EnhancedSessionState:
    def __init__(self):
        self.state = {}
        self.persistence = LocalStoragePersistence()
        
    def get(self, key, default=None):
        return self.state.get(key, default)
        
    def set(self, key, value, persist=False):
        self.state[key] = value
        if persist:
            self.persistence.save(key, value)
            
    def load_persistent(self):
        self.state.update(self.persistence.load_all())
```

**Component Library**:
```python
# Reusable components
class EnhancedComponents:
    @staticmethod
    def data_quality_badge(score: float) -> st.Component:
        """Create colored badge for data quality score"""
        color = "green" if score >= 90 else "yellow" if score >= 70 else "red"
        return st.markdown(f'<span style="background-color:{color}; color:white; padding:2px 6px; border-radius:3px;">{score}%</span>', unsafe_allow_html=True)
    
    @staticmethod
    def price_trend_indicator(trend: str) -> st.Component:
        """Create trend indicator with arrow"""
        icons = {"up": "📈", "down": "📉", "stable": "➡️"}
        return st.markdown(f'{icons.get(trend, "➡️")} {trend}')
```

#### 2. Historical Data Storage

**Database Initialization**:
```python
def initialize_database():
    conn = sqlite3.connect('insightflow.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            id TEXT PRIMARY KEY,
            product_id TEXT,
            timestamp DATETIME,
            price REAL,
            source_crawl_id TEXT,
            metadata TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_time ON historical_prices(product_id, timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON historical_prices(timestamp)')
    
    conn.commit()
    return conn
```

**Data Migration**:
```python
def migrate_parquet_to_database():
    """Migrate existing parquet data to SQLite database"""
    parquet_files = glob.glob("data/history/products_*.parquet")
    
    for file in parquet_files:
        df = pd.read_parquet(file)
        crawl_id = os.path.basename(file).replace('.parquet', '')
        
        for _, row in df.iterrows():
            # Extract price history if available
            # Store in historical_prices table
            pass
```

#### 3. Real-time Updates Implementation

**WebSocket Server** (Optional for advanced real-time):
```python
import asyncio
import websockets
import json

class DashboardWebSocketServer:
    def __init__(self):
        self.clients = set()
        
    async def register(self, websocket):
        self.clients.add(websocket)
        
    async def unregister(self, websocket):
        self.clients.remove(websocket)
        
    async def broadcast(self, message):
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])
            
    async def handle_price_update(self, product_id, new_price):
        message = json.dumps({
            "type": "price_update",
            "product_id": product_id,
            "price": new_price,
            "timestamp": datetime.now().isoformat()
        })
        await self.broadcast(message)
```

**Streamlit SSE Alternative** (Simpler):
```python
def setup_server_sent_events():
    """Set up Server-Sent Events for real-time updates"""
    @st.experimental_fragment
    def price_update_listener():
        if "price_updates" in st.session_state:
            updates = st.session_state.price_updates
            if updates:
                for update in updates:
                    st.toast(f"Price update: {update['product']} - {update['price']}")
                st.session_state.price_updates = []
```

#### 4. Alert Engine Implementation

**Core Engine**:
```python
class PriceAlertEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        self.active_alerts = self.load_active_alerts()
        
    def load_active_alerts(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM alerts WHERE active = 1")
        return [AlertConfig(**row) for row in cursor.fetchall()]
        
    def check_price_updates(self, price_updates: List[PriceUpdate]):
        triggered_alerts = []
        
        for alert in self.active_alerts:
            for update in price_updates:
                if update.product_id == alert.product_id:
                    if self.evaluate_condition(alert, update):
                        trigger = self.create_alert_trigger(alert, update)
                        triggered_alerts.append(trigger)
                        
        return triggered_alerts
        
    def evaluate_condition(self, alert: AlertConfig, update: PriceUpdate) -> bool:
        if alert.condition_type == "price_threshold":
            return update.price <= alert.threshold_value
        elif alert.condition_type == "percentage_change":
            # Get previous price from history
            previous_price = self.get_previous_price(alert.product_id)
            if previous_price:
                change = ((update.price - previous_price) / previous_price) * 100
                return abs(change) >= alert.threshold_value
        return False
```

#### 5. Export System Implementation

**PDF Report Generation**:
```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

class PDFExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
    def export_dashboard_report(self, data: pd.DataFrame, charts: List[bytes], options: ExportOptions) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Add title
        title = Paragraph("InsightFlow Dashboard Report", self.styles['Title'])
        story.append(title)
        
        # Add metadata
        metadata = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(metadata, self.styles['Normal']))
        
        # Add data table
        if not data.empty:
            table_data = [data.columns.tolist()] + data.values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            
        doc.build(story)
        return buffer.getvalue()
```

#### 6. Accessibility Implementation

**WCAG Compliance**:
```python
class AccessibilityManager:
    def ensure_keyboard_navigation(self):
        """Ensure all interactive elements are keyboard accessible"""
        # Streamlit components with tabindex
        pass
        
    def provide_alt_text(self, visual_elements):
        """Add alt text to charts and images"""
        for element in visual_elements:
            if hasattr(element, 'alt_text'):
                element.alt_text = self.generate_alt_text(element)
                
    def generate_alt_text(self, chart) -> str:
        """Generate descriptive alt text for charts"""
        if isinstance(chart, LineChart):
            return f"Line chart showing price trends over time. {chart.description}"
        elif isinstance(chart, BarChart):
            return f"Bar chart comparing {chart.comparison_dimension}. {chart.description}"
        return "Data visualization chart"
        
    def check_color_contrast(self, foreground, background):
        """Verify color contrast meets WCAG standards"""
        # Implement contrast ratio calculation
        pass
```

### Performance Considerations

#### 1. Data Loading Optimization

**Lazy Loading**:
```python
def lazy_load_product_data(product_ids: List[str], fields: List[str] = None):
    """Load only necessary product data"""
    if fields is None:
        fields = ['id', 'title', 'price', 'category']
        
    # Load from cache first
    cached = cache.get_many([f"product:{pid}" for pid in product_ids])
    
    # Load missing from database
    missing_ids = [pid for pid in product_ids if f"product:{pid}" not in cached]
    if missing_ids:
        db_data = load_from_database(missing_ids, fields)
        cache.set_many({f"product:{pid}": data for pid, data in db_data.items()})
        cached.update(db_data)
        
    return cached
```

#### 2. Chart Rendering Optimization

**Progressive Rendering**:
```python
def render_large_dataset_chart(data: pd.DataFrame, max_points: int = 1000):
    """Render large datasets with sampling for performance"""
    if len(data) > max_points:
        # Sample data for initial render
        sampled = data.sample(n=max_points, random_state=42)
        chart = create_chart(sampled)
        
        # Add note about sampling
        st.caption(f"Showing {max_points} of {len(data)} points for performance")
        return chart
    else:
        return create_chart(data)
```

#### 3. Database Query Optimization

**Index Strategy**:
- Composite indexes on frequently queried combinations
- Partial indexes for active/inactive data
- Materialized views for complex aggregations

**Query Optimization**:
```python
def optimized_price_history_query(product_id: str, start_date: datetime, end_date: datetime):
    """Optimized query for price history with date range"""
    query = """
        SELECT timestamp, price 
        FROM historical_prices 
        WHERE product_id = ? 
          AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp
    """
    
    # Use prepared statement with parameters
    cursor.execute(query, (product_id, start_date, end_date))
    return cursor.fetchall()
```

### Deployment Considerations

#### 1. Environment Configuration

**Configuration Management**:
```python
class DashboardConfig:
    def __init__(self):
        self.config = {
            'database': {
                'path': os.getenv('DB_PATH', 'insightflow.db'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', 10))
            },
            'cache': {
                'type': os.getenv('CACHE_TYPE', 'memory'),
                'redis_url': os.getenv('REDIS_URL', None)
            },
            'export': {
                'max_rows': int(os.getenv('EXPORT_MAX_ROWS', 10000)),
                'temp_dir': os.getenv('TEMP_DIR', '/tmp')
            },
            'alerts': {
                'check_interval': int(os.getenv('ALERT_INTERVAL', 60)),
                'max_notifications': int(os.getenv('MAX_NOTIFICATIONS', 100))
            }
        }
```

#### 2. Monitoring and Logging

**Structured Logging**:
```python
import structlog

logger = structlog.get_logger()

def log_dashboard_event(event_type: str, **kwargs):
    """Structured logging for dashboard events"""
    logger.info(
        event_type,
        timestamp=datetime.now().isoformat(),
        user_id=st.session_state.get('user_id', 'anonymous'),
        **kwargs
    )
```

**Performance Monitoring**:
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
        
    def track_operation(self, operation: str, duration: float):
        self.metrics[operation].append(duration)
        
    def get_performance_report(self):
        report = {}
        for operation, durations in self.metrics.items():
            report[operation] = {
                'count': len(durations),
                'avg': sum(durations) / len(durations),
                'p95': sorted(durations)[int(len(durations) * 0.95)],
                'max': max(durations)
            }
        return report
```

### Security Considerations

#### 1. Data Protection

**Sensitive Data Handling**:
- Encrypt user preferences and alert configurations
- Sanitize export file names to prevent path traversal
- Validate all user inputs for SQL injection prevention

**Access Control**:
```python
def validate_export_request(user_id: str, data_size: int) -> bool:
    """Validate export requests based on user permissions"""
    max_size = get_user_export_limit(user_id)
    return data_size <= max_size
```

#### 2. External Integration Security

**API Key Management**:
```python
class SecureAPIIntegration:
    def __init__(self):
        self.secrets = st.secrets if hasattr(st, 'secrets') else {}
        
    def get_telegram_bot_token(self):
        return self.secrets.get('telegram_bot_token')
        
    def get_email_credentials(self):
        return {
            'smtp_server': self.secrets.get('smtp_server'),
            'username': self.secrets.get('smtp_username'),
            'password': self.secrets.get('smtp_password')
        }
```

### Testing Strategy

#### 1. Unit Testing

**Test Coverage Goals**:
- Core data processing functions: 90%+
- Alert engine logic: 95%+
- Export formatting: 85%+
- UI component rendering: 80%+

**Test Structure**:
```python
class TestHistoricalPriceTracker:
    def test_get_price_history(self):
        tracker = HistoricalPriceTracker()
        history = tracker.get_price_history("product_123", TimeRange.LAST_30_DAYS)
        assert len(history) > 0
        assert all(isinstance(point, PricePoint) for point in history)
        
    def test_calculate_metrics_empty_history(self):
        tracker = HistoricalPriceTracker()
        metrics = tracker.calculate_metrics([])
        assert metrics.volatility == 0
        assert metrics.average_price == 0
```

#### 2. Integration Testing

**Test Scenarios**:
- End-to-end data flow from crawler to dashboard
- Alert triggering and notification delivery
- Export generation and file integrity
- Database migration and backward compatibility

#### 3. Performance Testing

**Load Testing**:
- Simulate multiple concurrent users
- Test with large datasets (100k+ products)
- Measure response times under load
- Identify memory leaks and bottlenecks

#### 4. Accessibility Testing

**Testing Tools**:
- axe-core for automated accessibility checks
- Screen reader compatibility testing
- Keyboard navigation verification
- Color contrast validation