# Implementation Guide for Outstanding Features

This guide provides detailed implementation plans for the three major features that are currently not implemented in the Cognitive Services Frontend project.

## Table of Contents
1. [Authentication & Authorization](#authentication--authorization)
2. [Usage Tracking & Billing](#usage-tracking--billing)
3. [Comprehensive Logging System](#comprehensive-logging-system)
4. [Implementation Priority](#implementation-priority)

## Authentication & Authorization

### Overview
Currently, all API endpoints are publicly accessible without any authentication. This is a critical security issue for production deployment.

### Implementation Plan

#### 1. Backend Authentication System

```python
# backend/services/auth/service.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = config.JWT_SECRET_KEY
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
```

#### 2. User Model and Database Schema

```python
# backend/models/auth_models.py
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    key_hash = Column(String, unique=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    is_active = Column(Boolean, default=True)
```

#### 3. Authentication Endpoints

```python
# backend/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register")
async def register(user: UserCreate):
    # Check if user exists
    # Hash password
    # Create user in database
    # Return user info
    pass

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate user
    # Create access token
    # Update last_login
    # Return token
    pass

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token
    # Return user info
    pass
```

#### 4. Protect Existing Endpoints

```python
# backend/api/document_intelligence.py
from fastapi import Depends
from .auth import get_current_user

@router.post("/process")
async def process_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),  # Add this
    background_tasks: BackgroundTasks
):
    # Existing logic
    pass
```

#### 5. Frontend Authentication

```javascript
// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/authService'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  
  async function login(credentials) {
    const response = await authService.login(credentials)
    token.value = response.access_token
    localStorage.setItem('token', response.access_token)
    await fetchUser()
  }
  
  async function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }
  
  return { user, token, isAuthenticated, isAdmin, login, logout }
})
```

### Database Requirements
- PostgreSQL or MongoDB for user storage
- Redis for session management (optional)
- Database migrations with Alembic

### Security Considerations
- Use HTTPS only
- Implement rate limiting on auth endpoints
- Add CAPTCHA for registration
- Email verification for new accounts
- Password reset functionality
- Two-factor authentication (optional)

## Usage Tracking & Billing

### Overview
Track API usage per user/organization for billing and analytics purposes.

### Implementation Plan

#### 1. Usage Tracking Model

```python
# backend/models/usage_models.py
class UsageRecord(Base):
    __tablename__ = "usage_records"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    service_type = Column(Enum(ServiceType))
    operation = Column(String)  # e.g., "document_process", "translate_text"
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Metrics
    input_size_bytes = Column(Integer)
    output_size_bytes = Column(Integer)
    processing_time_ms = Column(Integer)
    
    # Cost tracking
    azure_cost = Column(Float)  # Cost from Azure
    markup_percentage = Column(Float, default=20.0)
    total_cost = Column(Float)
    
    # Additional metadata
    job_id = Column(String)
    file_type = Column(String)
    page_count = Column(Integer)
    character_count = Column(Integer)
    
class UsageQuota(Base):
    __tablename__ = "usage_quotas"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    service_type = Column(Enum(ServiceType))
    
    # Limits
    monthly_request_limit = Column(Integer)
    monthly_byte_limit = Column(BigInteger)
    monthly_cost_limit = Column(Float)
    
    # Current usage
    current_requests = Column(Integer, default=0)
    current_bytes = Column(BigInteger, default=0)
    current_cost = Column(Float, default=0.0)
    
    # Period
    reset_date = Column(DateTime)
```

#### 2. Usage Tracking Service

```python
# backend/services/usage/service.py
class UsageTrackingService:
    def __init__(self):
        self.db = get_database_session()
    
    async def track_usage(
        self,
        user_id: str,
        service_type: ServiceType,
        operation: str,
        metrics: Dict[str, Any]
    ):
        # Calculate costs based on Azure pricing
        azure_cost = self.calculate_azure_cost(service_type, metrics)
        total_cost = azure_cost * (1 + MARKUP_PERCENTAGE / 100)
        
        # Create usage record
        record = UsageRecord(
            user_id=user_id,
            service_type=service_type,
            operation=operation,
            azure_cost=azure_cost,
            total_cost=total_cost,
            **metrics
        )
        
        # Check quotas
        await self.check_and_update_quotas(user_id, service_type, metrics, total_cost)
        
        # Save record
        self.db.add(record)
        await self.db.commit()
        
        # Send to analytics (optional)
        await self.send_to_analytics(record)
    
    async def check_quota(self, user_id: str, service_type: ServiceType) -> bool:
        quota = await self.db.query(UsageQuota).filter_by(
            user_id=user_id,
            service_type=service_type
        ).first()
        
        if not quota:
            return True  # No quota set
        
        return (
            quota.current_requests < quota.monthly_request_limit and
            quota.current_cost < quota.monthly_cost_limit
        )
```

#### 3. Integration with Existing Services

```python
# backend/api/document_intelligence.py
@router.post("/process")
async def process_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    usage_service: UsageTrackingService = Depends(get_usage_service)
):
    # Check quota
    if not await usage_service.check_quota(current_user.id, ServiceType.DOCUMENT_INTELLIGENCE):
        raise HTTPException(status_code=402, detail="Usage quota exceeded")
    
    # Process document
    result = await process_document_logic(file)
    
    # Track usage
    await usage_service.track_usage(
        user_id=current_user.id,
        service_type=ServiceType.DOCUMENT_INTELLIGENCE,
        operation="process_document",
        metrics={
            "input_size_bytes": file.size,
            "page_count": result.page_count,
            "processing_time_ms": result.processing_time
        }
    )
    
    return result
```

#### 4. Usage Dashboard API

```python
# backend/api/usage.py
@router.get("/usage/current")
async def get_current_usage(
    current_user: User = Depends(get_current_user),
    service_type: Optional[ServiceType] = None
):
    # Get current month usage
    # Return aggregated data
    pass

@router.get("/usage/history")
async def get_usage_history(
    current_user: User = Depends(get_current_user),
    start_date: datetime,
    end_date: datetime
):
    # Get historical usage
    # Return time-series data
    pass

@router.get("/usage/invoice/{month}")
async def get_invoice(
    month: str,
    current_user: User = Depends(get_current_user)
):
    # Generate invoice for the month
    # Return PDF or JSON
    pass
```

#### 5. Frontend Usage Dashboard

```vue
<!-- frontend/src/views/Usage.vue -->
<template>
  <div class="usage-dashboard">
    <h2>Usage & Billing</h2>
    
    <!-- Current Month Summary -->
    <div class="usage-summary">
      <div class="metric-card" v-for="service in services" :key="service.type">
        <h3>{{ service.name }}</h3>
        <div class="usage-bar">
          <div class="usage-fill" :style="{ width: service.percentage + '%' }"></div>
        </div>
        <p>{{ service.current }} / {{ service.limit }} requests</p>
        <p>${{ service.cost.toFixed(2) }} / ${{ service.costLimit.toFixed(2) }}</p>
      </div>
    </div>
    
    <!-- Usage Chart -->
    <UsageChart :data="chartData" />
    
    <!-- Invoice Download -->
    <button @click="downloadInvoice">Download Invoice</button>
  </div>
</template>
```

### Analytics Integration
- Time-series database (InfluxDB or TimescaleDB)
- Real-time dashboards (Grafana)
- Cost alerts and notifications
- Usage forecasting

## Comprehensive Logging System

### Overview
Implement structured logging with correlation IDs, performance metrics, and centralized log management.

### Implementation Plan

#### 1. Structured Logging Configuration

```python
# backend/utils/enhanced_logging.py
import structlog
from structlog.processors import JSONRenderer, TimeStamper, add_log_level
from pythonjsonlogger import jsonlogger

def setup_structured_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            add_correlation_id,
            add_user_context,
            add_request_context,
            JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to all log entries."""
    if correlation_id := get_correlation_id():
        event_dict["correlation_id"] = correlation_id
    return event_dict

def add_user_context(logger, method_name, event_dict):
    """Add user context to logs."""
    if user := get_current_user_context():
        event_dict["user_id"] = user.id
        event_dict["user_email"] = user.email
    return event_dict
```

#### 2. Performance Logging

```python
# backend/utils/performance_logging.py
from contextvars import ContextVar
from time import perf_counter
import structlog

performance_context: ContextVar[dict] = ContextVar('performance_context', default={})

class PerformanceLogger:
    def __init__(self, operation: str, **kwargs):
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
        self.logger = structlog.get_logger()
    
    def __enter__(self):
        self.start_time = perf_counter()
        self.logger.info(
            f"Starting {self.operation}",
            operation=self.operation,
            **self.kwargs
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (perf_counter() - self.start_time) * 1000
        
        if exc_type:
            self.logger.error(
                f"Failed {self.operation}",
                operation=self.operation,
                duration_ms=duration_ms,
                error=str(exc_val),
                error_type=exc_type.__name__,
                **self.kwargs
            )
        else:
            self.logger.info(
                f"Completed {self.operation}",
                operation=self.operation,
                duration_ms=duration_ms,
                **self.kwargs
            )
        
        # Add to performance context
        ctx = performance_context.get()
        ctx[self.operation] = duration_ms
        performance_context.set(ctx)
```

#### 3. Audit Logging

```python
# backend/models/audit_models.py
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"))
    
    # Action details
    action = Column(String)  # e.g., "document.process", "user.login"
    resource_type = Column(String)  # e.g., "document", "user"
    resource_id = Column(String)
    
    # Request context
    ip_address = Column(String)
    user_agent = Column(String)
    correlation_id = Column(String)
    
    # Change details
    old_value = Column(JSON)
    new_value = Column(JSON)
    
    # Result
    success = Column(Boolean)
    error_message = Column(String)

# backend/services/audit/service.py
class AuditService:
    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        success: bool = True,
        **kwargs
    ):
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            success=success,
            correlation_id=get_correlation_id(),
            **kwargs
        )
        
        await self.db.add(audit_log)
        await self.db.commit()
```

#### 4. Log Aggregation Setup

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - logging-net

  logstash:
    image: docker.elastic.co/logstash/logstash:8.0.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
    networks:
      - logging-net

  kibana:
    image: docker.elastic.co/kibana/kibana:8.0.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - logging-net

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.0.0
    volumes:
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - elasticsearch
    networks:
      - logging-net

volumes:
  elasticsearch-data:

networks:
  logging-net:
    driver: bridge
```

#### 5. Application Integration

```python
# backend/main.py
@app.middleware("http")
async def comprehensive_logging_middleware(request: Request, call_next):
    # Create performance logger
    with PerformanceLogger("http_request", 
                          method=request.method,
                          path=str(request.url.path)) as perf:
        
        # Set correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        set_correlation_id(correlation_id)
        
        # Log request
        logger.info(
            "HTTP Request",
            method=request.method,
            path=str(request.url.path),
            query_params=dict(request.query_params),
            headers={k: v for k, v in request.headers.items() if k.lower() != "authorization"}
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(
            "HTTP Response",
            status_code=response.status_code,
            method=request.method,
            path=str(request.url.path)
        )
        
        # Add correlation ID to response
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
```

### Monitoring and Alerting
- Set up alerts for error rates
- Monitor performance degradation
- Track API usage patterns
- Security event detection

## Implementation Priority

### Phase 1: Authentication (Weeks 1-2)
1. Set up database (PostgreSQL)
2. Implement user model and auth endpoints
3. Add JWT token validation
4. Update frontend with auth UI
5. Protect all API endpoints

### Phase 2: Logging (Weeks 3-4)
1. Implement structured logging
2. Add correlation IDs
3. Set up ELK stack
4. Configure log shipping
5. Create Kibana dashboards

### Phase 3: Usage Tracking (Weeks 5-6)
1. Design usage database schema
2. Implement usage tracking service
3. Integrate with all endpoints
4. Create billing calculations
5. Build usage dashboard UI

### Testing Strategy
- Unit tests for all new services
- Integration tests for auth flow
- Load testing for usage tracking
- Security testing for auth endpoints
- Log verification tests

### Migration Strategy
1. Deploy auth system with feature flag
2. Migrate existing users (if any)
3. Enable auth gradually
4. Monitor for issues
5. Full rollout

This implementation guide provides a comprehensive roadmap for adding the missing features. Each phase builds on the previous one, ensuring a stable and secure system.