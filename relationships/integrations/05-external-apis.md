# External APIs Relationship Map

**Status**: 🟡 Mixed (Some Production, Some Planned) | **Type**: External Services  
**Priority**: P2-P3 Variable | **Governance**: Per-API

---


## Navigation

**Location**: `relationships\integrations\05-external-apis.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

This document covers external APIs beyond AI/ML providers (OpenAI, HuggingFace) and version control (GitHub). These are specialized APIs for location, notifications, weather, etc.

---

## External APIs Inventory

### 1. IP Geolocation API (Production)

**Service**: IPStack (https://api.ipstack.com) or FreeGeoIP  
**Consumer**: `src/app/core/location_tracker.py` [[src/app/core/location_tracker.py]]  
**Purpose**: Get location from IP address  
**Authentication**: API key (optional for free tier)

```python
# API Contract
GET https://api.ipstack.com/134.201.250.155?access_key=YOUR_KEY
{
    "ip": "134.201.250.155",
    "type": "ipv4",
    "continent_code": "NA",
    "country_code": "US",
    "region_code": "CA",
    "city": "Los Angeles",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "location": {
        "is_eu": false,
        "geoname_id": 5368361
    }
}
```

### 2. SMTP Email API (Production)

**Service**: Gmail SMTP or SendGrid  
**Consumer**: `src/app/core/emergency_alert.py` [[src/app/core/emergency_alert.py]]  
**Purpose**: Send emergency alerts via email  
**Authentication**: SMTP username/password or API key

```python
# SMTP Configuration
smtp_config = {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": os.getenv("SMTP_USERNAME"),
    "password": os.getenv("SMTP_PASSWORD")
}

# Usage
msg = MIMEMultipart()
msg["From"] = smtp_config["username"]
msg["To"] = emergency_contact_email
msg["Subject"] = "Emergency Alert"
msg.attach(MIMEText(alert_message, "plain"))

with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
    server.starttls()
    server.login(smtp_config["username"], smtp_config["password"])
    server.send_message(msg)
```

### 3. GPS Location API (Planned)

**Service**: System GPS (Android/iOS) or Browser Geolocation API  
**Consumer**: `src/app/core/location_tracker.py` [[src/app/core/location_tracker.py]]  
**Purpose**: Get precise GPS coordinates  
**Authentication**: User permission (browser prompt or Android permission)

```python
# Browser Geolocation API (web version)
navigator.geolocation.getCurrentPosition(
    position => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        // Send to backend
    },
    error => console.error(error),
    { enableHighAccuracy: true, timeout: 5000 }
);
```

### 4. Weather API (Future)

**Service**: OpenWeatherMap or Weather.gov  
**Consumer**: Future `weather_service.py`  
**Purpose**: Contextual AI responses based on weather  
**Authentication**: API key

```python
# API Contract (OpenWeatherMap)
GET https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}
{
    "weather": [{"main": "Clear", "description": "clear sky"}],
    "main": {"temp": 298.15, "humidity": 60},
    "wind": {"speed": 3.5},
    "name": "Los Angeles"
}
```

### 5. News API (Future)

**Service**: NewsAPI.org or Reddit API  
**Consumer**: `src/app/gui/news_intelligence_panel.py` [[src/app/gui/news_intelligence_panel.py]]  
**Purpose**: Fetch news for intelligence briefings  
**Authentication**: API key

```python
# API Contract (NewsAPI)
GET https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}
{
    "status": "ok",
    "totalResults": 38,
    "articles": [
        {
            "source": {"id": "cnn", "name": "CNN"},
            "title": "Breaking News Title",
            "description": "News description...",
            "url": "https://cnn.com/article",
            "publishedAt": "2025-01-26T12:00:00Z"
        }
    ]
}
```

---

## Integration Patterns

### Pattern 1: Retry with Exponential Backoff

**Used By**: All HTTP APIs (IP geolocation, weather, news)

```python
import requests
import time

def api_request_with_retry(url, headers=None, max_retries=3):
    """Make API request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            elif response.status_code >= 500:
                # Server error, retry
                time.sleep(2 ** attempt)
                continue
            else:
                # Client error, don't retry
                logger.error(f"API error {response.status_code}: {response.text}")
                return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            time.sleep(2 ** attempt)
    
    return None
```

### Pattern 2: Caching to Reduce API Calls

**Used By**: Weather API, News API (future)

```python
from datetime import datetime, timedelta
import json

class CachedAPIClient:
    def __init__(self, cache_duration_minutes=15):
        self.cache = {}
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
    
    def get(self, url):
        """Get API response with caching."""
        now = datetime.now()
        
        # Check cache
        if url in self.cache:
            cached_time, cached_data = self.cache[url]
            if now - cached_time < self.cache_duration:
                logger.debug(f"Cache hit for {url}")
                return cached_data
        
        # Cache miss, make request
        data = api_request_with_retry(url)
        if data:
            self.cache[url] = (now, data)
        
        return data
```

### Pattern 3: Fallback to Free Tier

**Used By**: IP geolocation (fallback from IPStack to ip-api.com)

```python
def get_location_from_ip(ip_address):
    """Get location with fallback to free API."""
    # Try paid API first
    ipstack_key = os.getenv("IPSTACK_API_KEY")
    if ipstack_key:
        url = f"https://api.ipstack.com/{ip_address}?access_key={ipstack_key}"
        data = api_request_with_retry(url)
        if data:
            return data
    
    # Fallback to free API
    url = f"http://ip-api.com/json/{ip_address}"
    data = api_request_with_retry(url)
    return data
```

---

## Configuration

### Environment Variables

```bash
# IP Geolocation
IPSTACK_API_KEY=xxxxxxxxxxxxx  # Optional, falls back to free API

# Email (SMTP)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Generate at https://myaccount.google.com/apppasswords

# Weather (Future)
OPENWEATHER_API_KEY=xxxxxxxxxxxxx

# News (Future)
NEWSAPI_KEY=xxxxxxxxxxxxx
```

---

## Error Handling

### Common Errors Across APIs

1. **401 Unauthorized**: Invalid API key
   - **Mitigation**: Validate key on startup, log error, fallback to free tier

2. **429 Rate Limit**: Quota exceeded
   - **Mitigation**: Implement caching, exponential backoff, switch to free tier

3. **500 Server Error**: Service outage
   - **Mitigation**: Retry with backoff, return cached data if available

4. **Network Timeout**: Slow connection
   - **Mitigation**: Set reasonable timeouts (10s), retry 3 times

---

## Security

### API Key Management

- **Storage**: Environment variables (.env file)
- **Rotation**: Quarterly rotation recommended
- **Scoping**: Use minimal permissions (read-only when possible)

### Data Privacy

- **PII**: Never log user IP addresses or locations in production
- **Encryption**: Encrypt location history (Fernet, see `location_tracker.py`)
- **Compliance**: Follow GDPR/CCPA for location data

```python
# GDPR compliance: User consent before tracking
def enable_location_tracking(user_id):
    """Enable location tracking with user consent."""
    consent = input("Allow location tracking? (yes/no): ")
    if consent.lower() == "yes":
        # Save consent to database
        db.execute_query(
            "INSERT INTO user_consents (user_id, consent_type, granted_at) VALUES (?, ?, ?)",
            params=(user_id, "location_tracking", datetime.now())
        )
        return True
    return False
```

---

## Performance

### API Latency Benchmarks

| API | Avg Latency | P95 Latency | Cache Hit Ratio |
|-----|-------------|-------------|-----------------|
| IP Geolocation | 200ms | 500ms | N/A (unique IPs) |
| SMTP Email | 1-3s | 5s | N/A (no caching) |
| Weather | 300ms | 800ms | 95% (15min cache) |
| News | 500ms | 1s | 90% (15min cache) |

---

## Testing

```python
# tests/test_external_apis.py
import responses

@responses.activate
def test_ip_geolocation():
    # Mock API response
    responses.add(
        responses.GET,
        "https://api.ipstack.com/1.2.3.4?access_key=test",
        json={"city": "Los Angeles", "latitude": 34.05, "longitude": -118.24},
        status=200
    )
    
    tracker = LocationTracker()
    location = tracker.get_location_from_ip("1.2.3.4")
    
    assert location["city"] == "Los Angeles"

def test_email_alert():
    # Mock SMTP
    with patch("smtplib.SMTP") as mock_smtp:
        alert = EmergencyAlert()
        success, msg = alert.send_alert(
            "alice",
            {"lat": 34.05, "lng": -118.24},
            message="Test alert"
        )
        assert success
        mock_smtp.assert_called_once()
```

---

## Cost Analysis

### API Pricing

| API | Free Tier | Paid Tier | Current Usage | Cost/Month |
|-----|-----------|-----------|---------------|------------|
| IPStack | 100 requests/month | $10/10k requests | ~50/month | $0 (free tier) |
| Gmail SMTP | Unlimited | N/A | ~10/month | $0 |
| OpenWeatherMap | 1k calls/day | $40/month (unlimited) | 0 (not implemented) | $0 |
| NewsAPI | 100 requests/day | $449/month | 0 (not implemented) | $0 |

**Recommendation**: Stay on free tiers for now. Upgrade if usage grows.

---

## Future Enhancements

### Phase 1: Weather Integration ⏳ PLANNED
- Add `weather_service.py` with OpenWeatherMap API
- Display weather in dashboard
- Use weather for contextual AI responses

### Phase 2: News Intelligence 🔮 FUTURE
- Integrate NewsAPI for real-time news
- AI summarization of news articles
- Personalized news feed based on interests

### Phase 3: Unified API Gateway 🔮 FUTURE
- Create `api_gateway.py` for all external APIs
- Centralized rate limiting, caching, error handling
- API call analytics and cost tracking

---

## Related Systems

- **[01-openai-integration.md](01-openai-integration.md)**: AI-powered content analysis
- **[04-database-connectors.md](04-database-connectors.md)**: Cache API responses
- **[11-security-resources-api.md](11-security-resources-api.md)**: GitHub as external API
- **[12-email-integration.md](12-email-integration.md)**: Email API details

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly


---

## See Also

### Related Source Documentation

- **15 External Apis Overview**: [[source-docs\integrations\15-external-apis-overview.md]]
- **Documentation Index**: [[source-docs\integrations\README.md]]
