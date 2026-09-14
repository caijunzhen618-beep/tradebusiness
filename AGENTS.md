# 货运代理业务管理系统 - Python 代码开发规范

## 一、项目代码规范总则

### 1.1 编码标准
- 严格遵循 **PEP 8** 规范
- 使用 **Black** 进行代码格式化
- 使用 **isort** 管理 import 语句
- 使用 **pylint** 进行代码质量检查
- 类型注解遵循 **PEP 484**，使用 **mypy** 进行类型检查

### 1.2 代码风格要求
```python
# ✅ 正确示例
from typing import List, Optional
from datetime import datetime

class CustomerService:
    """客户服务类，处理客户相关业务逻辑"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_customer(
        self, 
        customer_id: str,
        include_contacts: bool = False
    ) -> Optional[Customer]:
        """
        获取客户信息
        
        Args:
            customer_id: 客户ID
            include_contacts: 是否包含联系人信息
            
        Returns:
            Customer对象或None
            
        Raises:
            CustomerNotFound: 当客户不存在时
        """
        pass

# ❌ 错误示例
class customerservice:  # 类名应使用大驼峰
    def __init__(self,db):  # 运算符两边应有空格
        self.db=db
        
    def getcustomer(self,customer_id,include_contacts=False):  # 函数名应使用小写下划线，参数间应有空格
        pass  # 缺少文档字符串
```

## 二、项目结构与文件组织规范

### 2.1 目录结构要求
```python
# ✅ 正确的目录组织
app/
├── api/              # API路由层（薄层，仅处理请求/响应）
├── services/         # 业务逻辑层（核心业务代码）
├── repositories/     # 数据访问层（数据库操作）
├── models/           # 数据库模型（ORM）
├── schemas/          # Pydantic模式（请求/响应验证）
├── core/             # 核心配置和工具
├── utils/            # 工具函数
└── tasks/            # 异步任务
```

### 2.2 分层架构原则

#### API层（app/api/）
```python
# ✅ 正确：API层应该很薄，只负责处理HTTP
from fastapi import APIRouter, Depends
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerResponse, CustomerCreate
from app.api.deps import get_current_user, get_customer_service

router = APIRouter()

@router.post("/", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """创建客户"""
    customer = await customer_service.create_customer(
        customer_data, 
        created_by=current_user.id
    )
    return customer

# ❌ 错误：不要在API层写业务逻辑
@router.post("/")
async def create_customer(customer_data: CustomerCreate):
    # 错误：直接在API层操作数据库
    customer = Customer(**customer_data.dict())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
```

#### Service层（app/services/）
```python
# ✅ 正确：业务逻辑应该在Service层
from typing import Optional
from app.models.customer import Customer
from app.repositories.customer_repo import CustomerRepository
from app.utils.email_validator import validate_email

class CustomerService:
    """客户业务逻辑"""
    
    def __init__(self, repo: CustomerRepository):
        self.repo = repo
    
    async def create_customer(
        self, 
        customer_data: CustomerCreate,
        created_by: str
    ) -> Customer:
        """创建客户，包含业务验证"""
        
        # 业务规则验证
        if not validate_email(customer_data.email):
            raise InvalidEmailException(customer_data.email)
        
        # 检查是否已存在
        existing = await self.repo.get_by_email(customer_data.email)
        if existing:
            raise DuplicateCustomerException(customer_data.email)
        
        # 创建客户
        customer = await self.repo.create(
            customer_data, 
            created_by=created_by
        )
        
        # 发送欢迎邮件（业务流程）
        await self._send_welcome_email(customer)
        
        return customer
    
    async def _send_welcome_email(self, customer: Customer):
        """私有辅助方法"""
        pass
```

#### Repository层（app/repositories/）
```python
# ✅ 正确：Repository只负责数据访问
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer

class CustomerRepository:
    """客户数据访问层"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """通过ID获取客户"""
        result = await self.session.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Customer]:
        """通过邮箱获取客户"""
        result = await self.session.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self, 
        customer_data: CustomerCreate,
        created_by: str
    ) -> Customer:
        """创建客户"""
        customer = Customer(
            **customer_data.dict(),
            created_by=created_by
        )
        self.session.add(customer)
        await self.session.flush()
        return customer
```

## 三、命名规范

### 3.1 文件命名
```python
# ✅ 正确
user_service.py       # 使用小写下划线
customer_repository.py
email_validator.py

# ❌ 错误
userService.py        # 不要用驼峰
Customer-repo.py      # 不要用连字符
```

### 3.2 类命名
```python
# ✅ 正确：使用大驼峰（PascalCase）
class CustomerService:
    pass

class EmailValidator:
    pass

class APIException:
    pass

# ❌ 错误
class customer_service:  # 小写下划线用于函数/变量
    pass
```

### 3.3 函数命名
```python
# ✅ 正确：使用小写下划线（snake_case）
def get_customer_by_id(customer_id: str):
    pass

async def create_customer(customer_data: dict):
    pass

def validate_email_format(email: str) -> bool:
    pass

# ❌ 错误
def getCustomerByID():  # 不要用驼峰
    pass
```

### 3.4 变量命名
```python
# ✅ 正确
customer_id = "123"
user_name = "John"
is_active = True
max_retries = 3

# 常量使用大写
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20
API_BASE_URL = "https://api.example.com"

# ❌ 错误
customerId = "123"   # 不要用驼峰
MAXRETRY = 3         # 常量应用大写下划线
```

### 3.5 私有成员命名
```python
class CustomerService:
    def __init__(self):
        self._cache = {}  # 私有属性，单下划线前缀
        self.__api_key = "xxx"  # 强私有，双下划线（name mangling）
    
    def _validate_data(self, data: dict):  # 私有方法，单下划线前缀
        pass
```

## 四、类型注解规范

### 4.1 函数类型注解
```python
# ✅ 正确：完整的类型注解
from typing import List, Optional, Dict
from datetime import datetime

def get_customers(
    country: str,
    status: Optional[str] = None,
    limit: int = 20
) -> List[Customer]:
    """获取客户列表"""
    pass

async def create_order(
    customer_id: str,
    items: List[OrderItem],
    metadata: Optional[Dict[str, any]] = None
) -> Order:
    """创建订单"""
    pass

# ❌ 错误：缺少类型注解
def get_customers(country, status=None, limit=20):
    pass
```

### 4.2 使用TypedDict
```python
from typing import TypedDict

class CustomerAddress(TypedDict):
    """客户地址类型"""
    street: str
    city: str
    country: str
    postal_code: str

def format_address(address: CustomerAddress) -> str:
    pass
```

### 4.3 使用NewType
```python
from typing import NewType

# 创建特定类型的别名，提高代码可读性
CustomerId = NewType('CustomerId', str)
Email = NewType('Email', str)

def get_customer(customer_id: CustomerId) -> Customer:
    pass

# 使用时
get_customer(CustomerId("123"))  # 明确这是ID
```

## 五、异常处理规范

### 5.1 自定义异常
```python
# ✅ 正确：在 app/core/exceptions.py 中定义
class AppException(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: str = "ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

class CustomerNotFoundException(AppException):
    """客户不存在异常"""
    def __init__(self, customer_id: str):
        super().__init__(
            message=f"Customer {customer_id} not found",
            code="CUSTOMER_NOT_FOUND"
        )

class InvalidEmailException(AppException):
    """无效邮箱异常"""
    def __init__(self, email: str):
        super().__init__(
            message=f"Invalid email: {email}",
            code="INVALID_EMAIL"
        )

# 使用
from app.core.exceptions import CustomerNotFoundException

async def get_customer(customer_id: str) -> Customer:
    customer = await repo.get_by_id(customer_id)
    if not customer:
        raise CustomerNotFoundException(customer_id)
    return customer
```

### 5.2 异常处理
```python
# ✅ 正确：捕获具体异常
import logging

logger = logging.getLogger(__name__)

async def send_customer_email(customer_id: str):
    try:
        customer = await customer_service.get_customer(customer_id)
        await email_service.send_email(customer.email)
    except CustomerNotFoundException as e:
        logger.warning(f"Customer not found: {e.message}")
        raise
    except EmailServiceException as e:
        logger.error(f"Failed to send email: {e.message}")
        # 业务异常，向上抛出
        raise

# ❌ 错误：捕获过于宽泛
async def send_customer_email(customer_id: str):
    try:
        # ... 代码 ...
    except Exception:  # 不要这样做，会隐藏所有错误
        pass
```

## 六、数据库操作规范

### 6.1 使用SQLAlchemy异步
```python
# ✅ 正确：使用异步Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """使用异步查询"""
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_customers(
        self, 
        country: str,
        limit: int
    ) -> List[Customer]:
        """带条件的列表查询"""
        stmt = (
            select(Customer)
            .where(
                Customer.country == country,
                Customer.is_active == True
            )
            .order_by(Customer.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
```

### 6.2 使用Repository模式
```python
# ✅ 正确：Repository基类
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """Repository基类"""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """通过ID获取"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, **kwargs) -> ModelType:
        """创建"""
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj
    
    async def update(self, obj: ModelType, **kwargs) -> ModelType:
        """更新"""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.session.flush()
        return obj
    
    async def delete(self, obj: ModelType) -> None:
        """删除"""
        await self.session.delete(obj)

# 使用
class CustomerRepository(BaseRepository[Customer]):
    """客户Repository"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(Customer, session)
    
    async def get_by_email(self, email: str) -> Optional[Customer]:
        """通过邮箱获取"""
        result = await self.session.execute(
            select(Customer).where(Customer.email == email)
        )
        return result.scalar_one_or_none()
```

### 6.3 事务处理
```python
# ✅ 正确：使用事务
from sqlalchemy.ext.asyncio import AsyncSession

async def create_order_with_items(
    session: AsyncSession,
    customer_id: str,
    items: List[OrderItem]
) -> Order:
    """创建订单和订单项（事务）"""
    async with session.begin():
        # 创建订单
        order = Order(customer_id=customer_id)
        session.add(order)
        await session.flush()  # 获取order.id
        
        # 创建订单项
        for item_data in items:
            item = OrderItem(
                order_id=order.id,
                **item_data
            )
            session.add(item)
        
        # 自动提交（如果成功）或回滚（如果失败）
    
    return order
```

## 七、API设计规范

### 7.1 路由组织
```python
# ✅ 正确：按功能模块组织路由
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user, get_customer_service
from app.schemas.customer import CustomerResponse, CustomerCreate

router = APIRouter(prefix="/customers", tags=["customers"])

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 20,
    country: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """获取客户列表"""
    pass

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    current_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """获取客户详情"""
    pass

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """创建客户"""
    pass
```

### 7.2 依赖注入
```python
# ✅ 正确：使用依赖注入
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.customer_service import CustomerService
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_customer_service(
    db: AsyncSession = Depends(get_db)
) -> CustomerService:
    """获取客户服务实例"""
    return CustomerService(CustomerRepository(db))

# 在路由中使用
@router.get("/customers")
async def list_customers(
    current_user: User = Depends(get_current_user),  # 依赖注入
    customer_service: CustomerService = Depends(get_customer_service)  # 依赖注入
):
    pass
```

### 7.3 Pydantic Schema
```python
# ✅ 正确：使用Pydantic进行数据验证
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class CustomerBase(BaseModel):
    """客户基础Schema"""
    company_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, regex=r"^\+?[\d\s-]{10,20}$")
    country: str = Field(..., min_length=2, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    
    @validator('company_name')
    def validate_company_name(cls, v):
        """验证公司名称"""
        if not v.strip():
            raise ValueError("Company name cannot be empty")
        return v.strip()

class CustomerCreate(CustomerBase):
    """创建客户Schema"""
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class CustomerUpdate(BaseModel):
    """更新客户Schema（所有字段可选）"""
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = None

class CustomerResponse(CustomerBase):
    """客户响应Schema"""
    id: str
    status: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True  # 支持ORM对象转换
```

## 八、异步编程规范

### 8.1 异步函数定义
```python
# ✅ 正确：IO密集型操作使用异步
async def fetch_customer_data(customer_id: str) -> dict:
    """异步获取客户数据"""
    # HTTP请求
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/api/customers/{customer_id}") as resp:
            return await resp.json()

async def send_email_async(to: str, subject: str, body: str):
    """异步发送邮件"""
    pass

# 对于数据库操作
async def get_customer(repo: CustomerRepository, customer_id: str):
    """必须是异步的"""
    return await repo.get_by_id(customer_id)

# ❌ 错误：在异步函数中使用同步IO
async def get_customer_wrong(customer_id: str):
    # 不要在异步函数中使用requests（同步）
    response = requests.get(f"/api/customers/{customer_id}")  # 错误
    return response.json()
```

### 8.2 并发控制
```python
# ✅ 正确：使用asyncio.gather进行并发
import asyncio

async def send_bulk_emails(customers: List[Customer]):
    """批量发送邮件（并发）"""
    tasks = [
        send_email_async(c.email, "Hello", "Body")
        for c in customers
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果
    for customer, result in zip(customers, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to send to {customer.email}: {result}")
    
    return results

# ✅ 使用Semaphore控制并发数
async def scrape_websites(urls: List[str], max_concurrent: int = 10):
    """爬取网站（限制并发数）"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_with_limit(url: str):
        async with semaphore:
            return await scrape_url(url)
    
    tasks = [scrape_with_limit(url) for url in urls]
    return await asyncio.gather(*tasks)
```

## 九、日志规范

### 9.1 日志配置
```python
# ✅ 正确：使用Python logging模块
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, repo: CustomerRepository):
        self.repo = repo
        self.logger = logging.getLogger(__name__)
    
    async def create_customer(self, data: CustomerCreate):
        self.logger.info(f"Creating customer: {data.email}")
        
        try:
            customer = await self.repo.create(data)
            self.logger.info(f"Customer created successfully: {customer.id}")
            return customer
        except Exception as e:
            self.logger.error(f"Failed to create customer: {e}", exc_info=True)
            raise
```

### 9.2 日志级别使用
```python
# ✅ 正确：合理使用日志级别
logger.debug("Detailed debug information")  # 调试信息
logger.info("User logged in")  # 正常业务流程
logger.warning("API rate limit exceeded")  # 警告（不影响运行）
logger.error("Database connection failed")  # 错误（需要关注）
logger.critical("System shutdown")  # 严重错误

# 使用结构化日志
logger.info(
    "customer_created",
    extra={
        "customer_id": customer.id,
        "email": customer.email,
        "created_by": user_id
    }
)
```

## 十、测试规范

### 10.1 单元测试
```python
# ✅ 正确：使用pytest
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.customer_service import CustomerService
from app.core.exceptions import CustomerNotFoundException

@pytest.mark.asyncio
async def test_get_customer_success():
    """测试：成功获取客户"""
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_id = AsyncMock(return_value=Customer(id="123", name="Test"))
    service = CustomerService(mock_repo)
    
    # Act
    customer = await service.get_customer("123")
    
    # Assert
    assert customer.id == "123"
    mock_repo.get_by_id.assert_called_once_with("123")

@pytest.mark.asyncio
async def test_get_customer_not_found():
    """测试：客户不存在"""
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_id = AsyncMock(return_value=None)
    service = CustomerService(mock_repo)
    
    # Act & Assert
    with pytest.raises(CustomerNotFoundException):
        await service.get_customer("999")
```

### 10.2 集成测试
```python
# ✅ 正确：集成测试使用test database
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_customer_api():
    """测试：创建客户API"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/customers/",
            json={
                "company_name": "Test Company",
                "email": "test@example.com",
                "country": "Nigeria"
            },
            headers={"Authorization": "Bearer token"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["company_name"] == "Test Company"
    assert "id" in data
```

## 十一、文档字符串规范

### 11.1 Google风格文档字符串
```python
# ✅ 正确：使用Google风格
def get_customers(
    country: str,
    status: Optional[str] = None,
    limit: int = 20
) -> List[Customer]:
    """获取客户列表
    
    Args:
        country: 国家代码（如：NG, KE, ZA）
        status: 客户状态筛选（可选）。默认为None
        limit: 返回数量限制。默认为20
    
    Returns:
        客户对象列表
        
    Raises:
        ValueError: 当country参数无效时
        DatabaseError: 当数据库查询失败时
        
    Example:
        >>> customers = get_customers("NG", status="active", limit=10)
        >>> len(customers)
        10
    """
    pass
```

## 十二、性能优化规范

### 12.1 数据库查询优化
```python
# ✅ 正确：使用select_related减少查询次数
# 假设Customer和User是关联的
async def get_customers_with_users():
    """使用eager loading"""
    stmt = (
        select(Customer)
        .options(selectinload(Customer.assigned_user))  # 预加载关联
        .where(Customer.is_active == True)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

# ✅ 使用索引
class Customer(Base):
    __tablename__ = "customers"
    
    email = Column(String, index=True)  # 为常查询字段添加索引
    country = Column(String, index=True)
    status = Column(String, index=True)
```

### 12.2 缓存策略
```python
# ✅ 正确：使用Redis缓存
from redis import Redis
import json

class CustomerService:
    def __init__(self, repo: CustomerRepository, redis: Redis):
        self.repo = repo
        self.redis = redis
        self.cache_ttl = 3600  # 1小时
    
    async def get_customer(self, customer_id: str) -> Customer:
        """先查缓存，再查数据库"""
        # 尝试从缓存获取
        cache_key = f"customer:{customer_id}"
        cached = self.redis.get(cache_key)
        if cached:
            return Customer.parse_raw(cached)
        
        # 缓存未命中，查询数据库
        customer = await self.repo.get_by_id(customer_id)
        if customer:
            # 写入缓存
            self.redis.setex(
                cache_key,
                self.cache_ttl,
                customer.json()
            )
        
        return customer
```

## 十三、安全规范

### 13.1 敏感数据处理
```python
# ✅ 正确：不要记录敏感信息
async def process_payment(card_number: str, expiry: str):
    """处理支付"""
    # ❌ 不要这样做
    # logger.info(f"Processing payment: {card_number}")
    
    # ✅ 正确做法
    logger.info(f"Processing payment: ****-****-****-{card_number[-4:]}")
    
    # 使用环境变量存储敏感配置
    import os
    api_key = os.getenv("PAYMENT_API_KEY")  # 不要硬编码
    
# ✅ 正确：使用secrets module生成随机值
import secrets

def generate_api_key() -> str:
    """生成API密钥"""
    return secrets.token_urlsafe(32)

# ✅ 正确：密码哈希
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain, hashed)
```

### 13.2 SQL注入防护
```python
# ✅ SQLAlchemy的参数化查询自动防止SQL注入
# 这一点已经通过使用ORM得到保证

# 如果使用原生SQL（不推荐），务必使用参数化
# ❌ 错误：字符串拼接（SQL注入风险）
query = f"SELECT * FROM customers WHERE id = '{customer_id}'"

# ✅ 正确：参数化查询
query = text("SELECT * FROM customers WHERE id = :customer_id")
await session.execute(query, {"customer_id": customer_id})
```

## 十四、配置管理规范

### 14.1 使用pydantic-settings
```python
# ✅ 正确：配置类
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "TradeBusiness API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")
    
    # JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # 邮件
    SMTP_HOST: str = Field(..., env="SMTP_HOST")
    SMTP_PORT: int = 587
    SMTP_USER: str = Field(..., env="SMTP_USER")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    
    # 限流
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 使用
settings = Settings()

# 在代码中
database_url = settings.DATABASE_URL
```

## 十五、导入顺序规范

### 15.1 isort配置
```python
# ✅ 正确的导入顺序
# 1. 标准库
import os
import logging
from typing import List, Optional
from datetime import datetime

# 2. 第三方库
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis

# 3. 本地模块
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate
from app.repositories.customer_repo import CustomerRepository
```

## 十六、代码审查检查清单

在提交代码前，请检查：

- [ ] 代码符合PEP 8规范
- [ ] 所有函数都有类型注解
- [ ] 所有公开函数/方法都有文档字符串
- [ ] 异常处理恰当，没有裸的except
- [ ] 没有硬编码的敏感信息
- [ ] 日志级别使用正确
- [ ] 数据库查询使用了索引字段
- [ ] 异步函数正确使用async/await
- [ ] 没有同步IO阻塞异步代码
- [ ] 单元测试覆盖核心逻辑
- [ ] 没有导入但未使用的模块
- [ ] 变量命名清晰有意义

## 十七、常用工具和命令

```bash
# 代码格式化
black app/ tests/

# 导入排序
isort app/ tests/

# 类型检查
mypy app/

# 代码质量检查
pylint app/

# 运行测试
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=app --cov-report=html

# 依赖安全检查
pip-audit

# 代码格式检查
flake8 app/
```

---

## 使用建议

1. **始终遵循分层架构**：API → Service → Repository，不要跨层调用
2. **优先使用类型注解**：让IDE和类型检查器帮助你
3. **编写有意义的文档字符串**：说明"为什么"而不是"是什么"
4. **测试核心业务逻辑**：Service层需要良好的单元测试覆盖
5. **保持函数简短**：一个函数只做一件事，控制在50行以内
6. **使用依赖注入**：提高代码可测试性和可维护性
7. **异常要具体**：自定义异常类，不要使用通用Exception
8. **日志要有用**：记录关键业务节点和错误信息
9. **安全第一**：永远不要信任用户输入，永远不要记录敏感信息
10. **性能意识**：关注N+1查询，合理使用缓存
