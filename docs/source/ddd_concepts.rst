=============================================
Domain-Driven Design (DDD) Reference Guide
=============================================

Complete reference of DDD building blocks organized by architectural layer.

----

Architecture Layers Overview
=============================

::

    ┌─────────────────────────────────────────┐
    │      Interface/Presentation Layer       │  ← User-facing (API endpoints, controllers)
    ├─────────────────────────────────────────┤
    │         Application Layer               │  ← Use case orchestration
    ├─────────────────────────────────────────┤
    │           Domain Layer                  │  ← Business logic & rules (Core)
    ├─────────────────────────────────────────┤
    │       Infrastructure Layer              │  ← Technical implementation
    └─────────────────────────────────────────┘

----

1. Domain Layer (Core Business Logic)
======================================

The heart of the application. Contains business rules, entities, and domain logic. **Should have no dependencies on other layers.**

+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| Building Block         | Description                                      | When to Use                                | Key Characteristics                                   |
+========================+==================================================+============================================+=======================================================+
| **Entity**             | Object with unique identity that persists        | When you need to track something           | - Has unique ID                                       |
|                        | over time                                        | through state changes                      | - Mutable                                             |
|                        |                                                  |                                            | - Identity-based equality                             |
|                        |                                                  |                                            | - Contains business logic                             |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Value Object**       | Immutable object defined by its attributes       | Describing characteristics without         | - No unique ID                                        |
|                        |                                                  | identity                                   | - Immutable                                           |
|                        |                                                  |                                            | - Value-based equality                                |
|                        |                                                  |                                            | - Self-validating                                     |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Aggregate**          | Cluster of entities/VOs treated as a unit        | Enforcing consistency boundaries           | - Contains Aggregate Root                             |
|                        | for data changes                                 |                                            | - Transaction boundary                                |
|                        |                                                  |                                            | - Enforces invariants                                 |
|                        |                                                  |                                            | - Emits Domain Events                                 |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Aggregate Root**     | Entry point entity to an aggregate               | Controlling access to aggregate internals  | - Special entity                                      |
|                        |                                                  |                                            | - Gateway to aggregate                                |
|                        |                                                  |                                            | - Ensures consistency                                 |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Domain Event**       | Record of something that happened in the domain  | Communicating state changes                | - Immutable                                           |
|                        |                                                  |                                            | - Past tense naming                                   |
|                        |                                                  |                                            | - Contains event data                                 |
|                        |                                                  |                                            | - Timestamp                                           |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Domain Service**     | Stateless operation that doesn't belong          | Multi-entity operations or pure            | - Stateless                                           |
|                        | to an entity                                     | calculations                               | - Pure domain logic                                   |
|                        |                                                  |                                            | - No infrastructure concerns                          |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Repository**         | Abstract persistence contract for aggregates     | Defining how aggregates are persisted      | - Interface only (no implementation)                  |
| **Interface**          |                                                  |                                            | - Aggregate-focused                                   |
|                        |                                                  |                                            | - Collection-like API                                 |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Factory**            | Creates complex domain objects                   | Complex object construction with rules     | - Encapsulates creation logic                         |
|                        |                                                  |                                            | - Enforces invariants                                 |
|                        |                                                  |                                            | - Multiple creation paths                             |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Specification**      | Encapsulated business rule                       | Reusable validation/filtering rules        | - Boolean logic                                       |
|                        |                                                  |                                            | - Composable                                          |
|                        |                                                  |                                            | - Declarative                                         |
+------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+

Domain Layer Examples
---------------------

Entity Example
^^^^^^^^^^^^^^

.. code-block:: python

    from dataclasses import dataclass
    from datetime import datetime

    @dataclass
    class OrderItem:
        """Entity: Has identity (id), can change quantity"""
        id: int  # Identity
        order_id: int
        product_id: int
        quantity: int
        unit_price: float

        def increase_quantity(self, amount: int) -> None:
            """Business logic: increase quantity"""
            if amount <= 0:
                raise ValueError("Amount must be positive")
            self.quantity += amount

        def calculate_total(self) -> float:
            """Business logic: calculate line total"""
            return self.quantity * self.unit_price


Value Object Example
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Email:
        """Value Object: Immutable, validated email"""
        value: str

        def __post_init__(self):
            if "@" not in self.value or "." not in self.value:
                raise ValueError(f"Invalid email: {self.value}")

        def domain(self) -> str:
            return self.value.split("@")[1]

    @dataclass(frozen=True)
    class Money:
        """Value Object: Amount with currency"""
        amount: float
        currency: str = "USD"

        def add(self, other: "Money") -> "Money":
            if self.currency != other.currency:
                raise ValueError("Cannot add different currencies")
            return Money(self.amount + other.amount, self.currency)


Aggregate Example
^^^^^^^^^^^^^^^^^

.. code-block:: python

    from dataclasses import dataclass, field
    from typing import List
    from datetime import datetime

    @dataclass
    class Order(BaseAggregate):  # Aggregate Root
        """Order Aggregate: manages OrderItems, enforces business rules"""
        id: int
        customer_id: int
        status: str
        created_at: datetime
        items: List[OrderItem] = field(default_factory=list)

        def add_item(self, product_id: int, quantity: int, price: float) -> None:
            """Business rule: Add item and emit event"""
            if self.status == "completed":
                raise ValueError("Cannot modify completed order")

            # Check if item already exists
            for item in self.items:
                if item.product_id == product_id:
                    item.increase_quantity(quantity)
                    return

            # Add new item
            item = OrderItem(
                id=len(self.items) + 1,
                order_id=self.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=price
            )
            self.items.append(item)

            # Emit domain event
            self.add_event(OrderItemAddedEvent(
                order_id=self.id,
                product_id=product_id,
                quantity=quantity
            ))

        def calculate_total(self) -> float:
            """Business rule: Calculate order total"""
            return sum(item.calculate_total() for item in self.items)

        def complete(self) -> None:
            """Business rule: Complete order"""
            if not self.items:
                raise ValueError("Cannot complete empty order")
            if self.status == "completed":
                raise ValueError("Order already completed")

            self.status = "completed"
            self.add_event(OrderCompletedEvent(order_id=self.id))


Domain Event Example
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from dataclasses import dataclass
    from datetime import datetime

    @dataclass(frozen=True)
    class UserCreatedEvent(DomainEvent):
        """Event: User was created"""
        user_uuid: str
        email: str
        created_at: datetime

    @dataclass(frozen=True)
    class OrderCompletedEvent(DomainEvent):
        """Event: Order was completed"""
        order_id: int
        completed_at: datetime
        total_amount: float


Domain Service Example
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    class OrderPricingService:
        """Domain Service: Pricing doesn't belong to Order or Product alone"""

        def calculate_discounted_price(
            self,
            order: Order,
            customer: Customer,
            discount_rules: List[DiscountRule]
        ) -> Money:
            """Calculate price with discounts based on customer and order"""
            base_price = order.calculate_total()

            # Apply customer-specific discounts
            discount = 0.0
            for rule in discount_rules:
                if rule.applies_to(customer, order):
                    discount += rule.calculate_discount(base_price)

            return Money(base_price - discount)

    class PasswordHashingService:
        """Domain Service: Password hashing is pure domain logic"""

        def hash_password(self, raw_password: str) -> str:
            """Hash password using bcrypt"""
            import bcrypt
            return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

        def verify_password(self, raw_password: str, hashed: str) -> bool:
            """Verify password against hash"""
            import bcrypt
            return bcrypt.checkpw(raw_password.encode(), hashed.encode())


Repository Interface Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from abc import ABC, abstractmethod
    from typing import Optional, List

    class IUserRepository(ABC):
        """Repository Interface: Defined in domain, implemented in infrastructure"""

        @abstractmethod
        async def get_by_id(self, user_id: int) -> Optional[UserAggregate]:
            """Get user by ID"""
            pass

        @abstractmethod
        async def get_by_email(self, email: str) -> Optional[UserAggregate]:
            """Get user by email"""
            pass

        @abstractmethod
        async def save(self, user: UserAggregate) -> None:
            """Save user aggregate"""
            pass

        @abstractmethod
        async def delete(self, user_id: int) -> None:
            """Delete user"""
            pass

        @abstractmethod
        async def list_all(self, skip: int = 0, limit: int = 100) -> List[UserAggregate]:
            """List all users with pagination"""
            pass


Factory Example
^^^^^^^^^^^^^^^

.. code-block:: python

    from uuid import uuid4
    from datetime import datetime

    class UserFactory:
        """Factory: Complex user creation with different paths"""

        @staticmethod
        def create_guest() -> UserAggregate:
            """Create guest user with defaults"""
            return UserAggregate(
                id=0,
                uuid=str(uuid4()),
                email=f"guest_{uuid4().hex[:8]}@temp.com",
                is_guest=True,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                password_hashed=None,
                meta={"source": "guest_creation"}
            )

        @staticmethod
        def create_from_registration(
            email: str,
            password_hashed: str,
            first_name: str,
            last_name: str
        ) -> UserAggregate:
            """Create user from registration with validation"""
            if not email or "@" not in email:
                raise ValueError("Invalid email")

            return UserAggregate(
                id=0,
                uuid=str(uuid4()),
                email=email,
                password_hashed=password_hashed,
                first_name=first_name,
                last_name=last_name,
                is_guest=False,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                meta={"source": "registration"}
            )

        @staticmethod
        def create_from_oauth(
            provider: str,
            external_id: str,
            email: str,
            profile_data: dict
        ) -> UserAggregate:
            """Create user from OAuth provider"""
            return UserAggregate(
                id=0,
                uuid=str(uuid4()),
                email=email,
                password_hashed=None,  # No password for OAuth
                first_name=profile_data.get("first_name"),
                last_name=profile_data.get("last_name"),
                photo=profile_data.get("picture"),
                is_guest=False,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                meta={
                    "source": "oauth",
                    "provider": provider,
                    "external_id": external_id
                }
            )


Specification Example
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from abc import ABC, abstractmethod

    class Specification(ABC):
        """Base specification pattern"""

        @abstractmethod
        def is_satisfied_by(self, candidate) -> bool:
            pass

        def and_(self, other: "Specification") -> "AndSpecification":
            return AndSpecification(self, other)

        def or_(self, other: "Specification") -> "OrSpecification":
            return OrSpecification(self, other)

        def not_(self) -> "NotSpecification":
            return NotSpecification(self)


    class UserIsActiveSpec(Specification):
        """Check if user is active"""

        def is_satisfied_by(self, user: UserAggregate) -> bool:
            return user.is_active and not user.is_guest


    class UserCanPostSpec(Specification):
        """Check if user can create posts"""

        def __init__(self, min_account_age_days: int = 1):
            self.min_account_age_days = min_account_age_days

        def is_satisfied_by(self, user: UserAggregate) -> bool:
            from datetime import datetime, timedelta

            is_active = UserIsActiveSpec().is_satisfied_by(user)
            is_old_enough = (
                datetime.now() - user.created_at
                >= timedelta(days=self.min_account_age_days)
            )

            return is_active and is_old_enough


    class AndSpecification(Specification):
        """Composite AND specification"""

        def __init__(self, left: Specification, right: Specification):
            self.left = left
            self.right = right

        def is_satisfied_by(self, candidate) -> bool:
            return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


----

2. Application Layer (Use Case Orchestration)
==============================================

Coordinates domain objects to fulfill use cases. **Depends on domain layer, not infrastructure.**

+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| Building Block            | Description                                      | When to Use                                | Key Characteristics                                   |
+===========================+==================================================+============================================+=======================================================+
| **Application Service**   | Orchestrates use cases using domain objects      | Every user-facing feature/use case         | - Stateless                                           |
|                           |                                                  |                                            | - Transaction boundaries                              |
|                           |                                                  |                                            | - Coordinates domain objects                          |
|                           |                                                  |                                            | - No business logic                                   |
|                           |                                                  |                                            | - Handles events                                      |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **DTO (Data Transfer**    | Data container for transferring data             | Moving data across boundaries              | - No behavior                                         |
| **Object)**               | between layers                                   |                                            | - Validation rules                                    |
|                           |                                                  |                                            | - Serialization                                       |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Command**               | Request to change system state                   | CQRS pattern, async processing             | - Intent-revealing name                               |
|                           |                                                  |                                            | - Immutable                                           |
|                           |                                                  |                                            | - Contains all data needed                            |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Query**                 | Request to read data                             | CQRS pattern, read-only operations         | - No side effects                                     |
|                           |                                                  |                                            | - Returns DTOs                                        |
|                           |                                                  |                                            | - Optimized for reads                                 |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Command Handler**       | Executes a command                               | Processing commands in CQRS                | - One handler per command                             |
|                           |                                                  |                                            | - Contains use case logic                             |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Query Handler**         | Executes a query                                 | Processing queries in CQRS                 | - One handler per query                               |
|                           |                                                  |                                            | - Read-only operations                                |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+

Application Layer Examples
--------------------------

Application Service Example (Real from your project)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    class AppAuthService(AbstractBaseApplicationService):
        """Application Service: Orchestrates authentication use cases"""

        # Dependencies on domain services
        dom_users_svc_container: DomainUsersServiceContainer
        dom_auth_svc_container: DomainAuthServiceContainer

        @classmethod
        async def create_auth_user(cls, data: dict) -> Any:
            """Use case: Register new user"""
            # 1. Validate email
            email = data.get("email") or ""
            email_validated = validate_email(email)[1]

            # 2. Check if exists (application logic)
            is_exists = await cls.app_svc_container.users_service.is_exists(
                filter_data={"email": email_validated}
            )
            if is_exists:
                raise AlreadyExistsError(message="User already exists")

            # 3. Hash password (domain service)
            password = data.pop("password", None) or ""
            password_hashed = cls.dom_auth_svc_container.auth_service.get_password_hashed(password)
            data["password_hashed"] = password_hashed

            # 4. Create user (repository)
            return await cls.app_svc_container.users_service.create(data)

        @classmethod
        async def authenticate_user(cls, email: str, password: str) -> tuple[Any, TokenPair]:
            """Use case: Authenticate user and return tokens"""
            # 1. Validate email
            email_validated = validate_email(email)[1]

            # 2. Get user (repository)
            user = await cls.app_svc_container.users_service.get_first(
                filter_data={"email": email_validated}
            )

            # 3. Verify password (domain service)
            is_valid = cls.dom_auth_svc_container.auth_service.verify_password(
                password, user.password_hashed
            )
            if not user or not is_valid:
                raise ValidationError(message="Invalid credentials")

            # 4. Create tokens (domain service)
            tokens = cls.dom_auth_svc_container.jwt_service.create_token_pair(user.uuid)

            return user, tokens


Command/Query Examples (CQRS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from dataclasses import dataclass

    # Commands (write operations)
    @dataclass(frozen=True)
    class CreateUserCommand:
        """Command: Create a new user"""
        email: str
        password: str
        first_name: str
        last_name: str

    @dataclass(frozen=True)
    class UpdateUserProfileCommand:
        """Command: Update user profile"""
        user_id: int
        first_name: str | None = None
        last_name: str | None = None
        phone: str | None = None

    # Queries (read operations)
    @dataclass(frozen=True)
    class GetUserByIdQuery:
        """Query: Get user by ID"""
        user_id: int

    @dataclass(frozen=True)
    class ListUsersQuery:
        """Query: List users with filters"""
        is_active: bool | None = None
        skip: int = 0
        limit: int = 100


    # Command Handler
    class CreateUserCommandHandler:
        """Handle CreateUserCommand"""

        def __init__(self, user_repo: IUserRepository, auth_service: PasswordHashingService):
            self.user_repo = user_repo
            self.auth_service = auth_service

        async def handle(self, command: CreateUserCommand) -> int:
            """Execute command and return user ID"""
            # Hash password
            password_hashed = self.auth_service.hash_password(command.password)

            # Create user aggregate
            user = UserFactory.create_from_registration(
                email=command.email,
                password_hashed=password_hashed,
                first_name=command.first_name,
                last_name=command.last_name
            )

            # Save to repository
            await self.user_repo.save(user)

            # Publish events
            for event in user.get_events():
                await event_publisher.publish(event)
            user.events_clear()

            return user.id


    # Query Handler
    class GetUserByIdQueryHandler:
        """Handle GetUserByIdQuery"""

        def __init__(self, user_repo: IUserRepository):
            self.user_repo = user_repo

        async def handle(self, query: GetUserByIdQuery) -> UserDTO:
            """Execute query and return DTO"""
            user = await self.user_repo.get_by_id(query.user_id)
            if not user:
                raise NotFoundError(f"User {query.user_id} not found")

            return UserDTO.from_aggregate(user)


DTO Example
^^^^^^^^^^^

.. code-block:: python

    from dataclasses import dataclass
    from datetime import datetime

    @dataclass
    class UserDTO:
        """DTO: Transfer user data to presentation layer"""
        id: int
        uuid: str
        email: str
        first_name: str | None
        last_name: str | None
        is_active: bool
        created_at: datetime

        @classmethod
        def from_aggregate(cls, user: UserAggregate) -> "UserDTO":
            """Convert aggregate to DTO"""
            return cls(
                id=user.id,
                uuid=user.uuid,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                created_at=user.created_at
            )

        def to_dict(self) -> dict:
            """Serialize for API response"""
            return {
                "id": self.id,
                "uuid": self.uuid,
                "email": self.email,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "is_active": self.is_active,
                "created_at": self.created_at.isoformat()
            }


----

3. Infrastructure Layer (Technical Implementation)
==================================================

Provides technical capabilities. **Implements interfaces defined in domain layer.**

+-------------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| Building Block                | Description                                      | When to Use                                | Key Characteristics                                   |
+===============================+==================================================+============================================+=======================================================+
| **Repository**                | Concrete persistence implementation              | Implementing domain repository interfaces  | - Database access                                     |
| **Implementation**            |                                                  |                                            | - ORM mapping                                         |
|                               |                                                  |                                            | - Query optimization                                  |
+-------------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Infrastructure Service**    | Technical services (email, SMS, logging)         | External integrations                      | - No domain logic                                     |
|                               |                                                  |                                            | - Adapters to external systems                        |
+-------------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Event Publisher**           | Publishes domain events to message bus           | Event-driven architecture                  | - Message broker integration                          |
|                               |                                                  |                                            | - Async processing                                    |
+-------------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Mapper/Adapter**            | Converts between domain and infrastructure       | Translating between layers                 | - ORM entities ↔ Aggregates                           |
|                               | models                                           |                                            | - External API ↔ Domain                               |
+-------------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+

Infrastructure Layer Examples
-----------------------------

Repository Implementation Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from typing import Optional, List

    class UserRepository(IUserRepository):
        """Repository Implementation: SQLAlchemy-based persistence"""

        def __init__(self, session: AsyncSession):
            self.session = session

        async def get_by_id(self, user_id: int) -> Optional[UserAggregate]:
            """Get user from database"""
            # Query ORM model
            result = await self.session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()

            if not user_model:
                return None

            # Convert ORM model to aggregate
            return self._to_aggregate(user_model)

        async def save(self, user: UserAggregate) -> None:
            """Save user to database"""
            # Convert aggregate to ORM model
            user_model = self._to_model(user)

            # Save to database
            self.session.add(user_model)
            await self.session.flush()

            # Update aggregate ID if new
            if user.id == 0:
                user.id = user_model.id

        async def list_all(self, skip: int = 0, limit: int = 100) -> List[UserAggregate]:
            """List users with pagination"""
            result = await self.session.execute(
                select(UserModel).offset(skip).limit(limit)
            )
            user_models = result.scalars().all()

            return [self._to_aggregate(model) for model in user_models]

        def _to_aggregate(self, model: UserModel) -> UserAggregate:
            """Map ORM model to domain aggregate"""
            return UserAggregate(
                id=model.id,
                uuid=model.uuid,
                email=model.email,
                password_hashed=model.password_hashed,
                first_name=model.first_name,
                last_name=model.last_name,
                is_active=model.is_active,
                is_guest=model.is_guest,
                created_at=model.created_at,
                updated_at=model.updated_at,
                meta=model.meta or {}
            )

        def _to_model(self, aggregate: UserAggregate) -> UserModel:
            """Map domain aggregate to ORM model"""
            return UserModel(
                id=aggregate.id if aggregate.id else None,
                uuid=aggregate.uuid,
                email=aggregate.email,
                password_hashed=aggregate.password_hashed,
                first_name=aggregate.first_name,
                last_name=aggregate.last_name,
                is_active=aggregate.is_active,
                is_guest=aggregate.is_guest,
                meta=aggregate.meta
            )


Infrastructure Service Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    class EmailService:
        """Infrastructure Service: Send emails via external provider"""

        def __init__(self, smtp_config: dict):
            self.smtp_config = smtp_config

        async def send_email(self, to: str, subject: str, body: str) -> None:
            """Send email using SMTP"""
            import aiosmtplib
            from email.message import EmailMessage

            message = EmailMessage()
            message["From"] = self.smtp_config["from"]
            message["To"] = to
            message["Subject"] = subject
            message.set_content(body)

            await aiosmtplib.send(
                message,
                hostname=self.smtp_config["host"],
                port=self.smtp_config["port"],
                username=self.smtp_config["username"],
                password=self.smtp_config["password"]
            )


    class SMSService:
        """Infrastructure Service: Send SMS via Twilio"""

        def __init__(self, twilio_client):
            self.client = twilio_client

        async def send_sms(self, to: str, message: str) -> None:
            """Send SMS using Twilio"""
            await self.client.messages.create(
                to=to,
                from_="+1234567890",
                body=message
            )


Event Publisher Example
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    class RabbitMQEventPublisher:
        """Event Publisher: Publish domain events to RabbitMQ"""

        def __init__(self, connection):
            self.connection = connection

        async def publish(self, event: DomainEvent) -> None:
            """Publish event to message queue"""
            import json

            channel = await self.connection.channel()

            # Serialize event
            event_data = {
                "event_id": event.id,
                "event_type": event.__class__.__name__,
                "occurred_at": event.occurred_at.isoformat(),
                "payload": event.to_dict()
            }

            # Publish to exchange
            await channel.basic_publish(
                exchange="domain_events",
                routing_key=event.__class__.__name__,
                body=json.dumps(event_data).encode()
            )


----

4. Interface/Presentation Layer (User Interface)
=================================================

Handles user interaction. **Depends on application layer.**

+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| Building Block            | Description                                      | When to Use                                | Key Characteristics                                   |
+===========================+==================================================+============================================+=======================================================+
| **Controller/Endpoint**   | Handles HTTP requests                            | Web APIs, REST endpoints                   | - Request validation                                  |
|                           |                                                  |                                            | - Calls application services                          |
|                           |                                                  |                                            | - Returns responses                                   |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **View Model**            | Data prepared for UI display                     | Presenting data to users                   | - UI-specific structure                               |
|                           |                                                  |                                            | - Formatted data                                      |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+
| **Request/Response**      | API contract definitions                         | API endpoints                              | - Input validation                                    |
| **Models**                |                                                  |                                            | - Serialization                                       |
+---------------------------+--------------------------------------------------+--------------------------------------------+-------------------------------------------------------+

Interface Layer Examples
------------------------

API Controller Example
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from fastapi import APIRouter, Depends, HTTPException, status
    from pydantic import BaseModel

    router = APIRouter(prefix="/api/users")


    # Request/Response Models
    class RegisterUserRequest(BaseModel):
        """API Request: User registration"""
        email: str
        password: str
        first_name: str
        last_name: str


    class UserResponse(BaseModel):
        """API Response: User data"""
        id: int
        uuid: str
        email: str
        first_name: str | None
        last_name: str | None
        is_active: bool


    class TokenResponse(BaseModel):
        """API Response: Authentication tokens"""
        access_token: str
        refresh_token: str
        token_type: str = "bearer"


    # Controllers/Endpoints
    @router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
    async def register_user(
        request: RegisterUserRequest,
        auth_service: AppAuthService = Depends()
    ):
        """Endpoint: Register new user"""
        try:
            # Call application service
            user = await auth_service.create_auth_user(request.dict())

            # Return response
            return UserResponse(
                id=user.id,
                uuid=user.uuid,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active
            )
        except AlreadyExistsError as e:
            raise HTTPException(status_code=400, detail=str(e))


    @router.post("/login", response_model=TokenResponse)
    async def login(
        email: str,
        password: str,
        auth_service: AppAuthService = Depends()
    ):
        """Endpoint: Authenticate user"""
        try:
            # Call application service
            user, tokens = await auth_service.authenticate_user(email, password)

            # Return tokens
            return TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token
            )
        except ValidationError as e:
            raise HTTPException(status_code=401, detail="Invalid credentials")


----

Layer Dependencies
==================

::

    Interface Layer
        ↓ depends on
    Application Layer
        ↓ depends on
    Domain Layer ← Core (no dependencies)
        ↑ implemented by
    Infrastructure Layer

**Key Rules:**

- Domain layer has NO dependencies on other layers
- Infrastructure implements domain interfaces
- Application orchestrates domain objects
- Interface calls application services

----

Quick Decision Guide
====================

"Where does this code belong?"
------------------------------

+--------------------------------------------------------+--------+------------------+
| Question                                               | Answer | Layer            |
+========================================================+========+==================+
| Is it a business rule or concept?                      | Yes    | **Domain**       |
+--------------------------------------------------------+--------+------------------+
| Does it coordinate multiple domain objects?            | Yes    | **Application**  |
+--------------------------------------------------------+--------+------------------+
| Does it touch a database or external API?              | Yes    | **Infrastructure**|
+--------------------------------------------------------+--------+------------------+
| Does it handle HTTP requests/responses?                | Yes    | **Interface**    |
+--------------------------------------------------------+--------+------------------+

"Which building block do I use?"
--------------------------------

+--------------------------------------------------------+---------------------------+
| Need                                                   | Use                       |
+========================================================+===========================+
| Track something with identity that changes             | **Entity**                |
+--------------------------------------------------------+---------------------------+
| Describe something immutable                           | **Value Object**          |
+--------------------------------------------------------+---------------------------+
| Group related entities with consistency rules          | **Aggregate**             |
+--------------------------------------------------------+---------------------------+
| Record something that happened                         | **Domain Event**          |
+--------------------------------------------------------+---------------------------+
| Multi-entity business logic                            | **Domain Service**        |
+--------------------------------------------------------+---------------------------+
| Orchestrate a use case                                 | **Application Service**   |
+--------------------------------------------------------+---------------------------+
| Save/load aggregates                                   | **Repository**            |
+--------------------------------------------------------+---------------------------+
| Complex object creation                                | **Factory**               |
+--------------------------------------------------------+---------------------------+
| Reusable business rule                                 | **Specification**         |
+--------------------------------------------------------+---------------------------+

----

Common Patterns
===============

Pattern: Aggregate with Events
-------------------------------

.. code-block:: python

    @dataclass
    class User(BaseAggregate):
        id: int
        email: str
        password_hashed: str

        def change_password(self, new_password_hashed: str) -> None:
            """Change password and emit event"""
            old_hash = self.password_hashed
            self.password_hashed = new_password_hashed

            # Emit event
            self.add_event(UserPasswordChangedEvent(
                user_id=self.id,
                changed_at=datetime.now()
            ))


Pattern: Application Service with Transaction
----------------------------------------------

.. code-block:: python

    class OrderApplicationService:
        def __init__(
            self,
            order_repo: IOrderRepository,
            inventory_service: InventoryService,
            event_publisher: EventPublisher
        ):
            self.order_repo = order_repo
            self.inventory_service = inventory_service
            self.event_publisher = event_publisher

        async def place_order(self, command: PlaceOrderCommand) -> int:
            """Use case: Place order (transactional)"""
            async with transaction():
                # 1. Create order aggregate
                order = OrderFactory.create_new(command.customer_id)

                # 2. Add items
                for item in command.items:
                    order.add_item(item.product_id, item.quantity, item.price)

                # 3. Reserve inventory (domain service)
                for item in order.items:
                    await self.inventory_service.reserve(item.product_id, item.quantity)

                # 4. Complete order
                order.complete()

                # 5. Save aggregate
                await self.order_repo.save(order)

                # 6. Publish events
                for event in order.get_events():
                    await self.event_publisher.publish(event)
                order.events_clear()

                return order.id


Pattern: Repository with Mapper
--------------------------------

.. code-block:: python

    class ProductRepository(IProductRepository):
        def __init__(self, session: AsyncSession):
            self.session = session
            self.mapper = ProductMapper()

        async def get_by_id(self, product_id: int) -> Optional[Product]:
            model = await self.session.get(ProductModel, product_id)
            return self.mapper.to_domain(model) if model else None

        async def save(self, product: Product) -> None:
            model = self.mapper.to_persistence(product)
            self.session.add(model)


    class ProductMapper:
        """Mapper: Convert between domain and persistence models"""

        def to_domain(self, model: ProductModel) -> Product:
            return Product(
                id=model.id,
                name=model.name,
                price=Money(model.price, model.currency),
                stock=model.stock
            )

        def to_persistence(self, product: Product) -> ProductModel:
            return ProductModel(
                id=product.id,
                name=product.name,
                price=product.price.amount,
                currency=product.price.currency,
                stock=product.stock
            )


----

Anti-Patterns to Avoid
=======================

+--------------------------------+--------------------------------------------------+------------------------------------------------------+
| Anti-Pattern                   | Problem                                          | Solution                                             |
+================================+==================================================+======================================================+
| Anemic Domain Model            | Entities with only getters/setters, no behavior  | Move logic from services into entities               |
+--------------------------------+--------------------------------------------------+------------------------------------------------------+
| God Object                     | One huge entity doing everything                 | Split into multiple aggregates                       |
+--------------------------------+--------------------------------------------------+------------------------------------------------------+
| Domain Logic in Controllers    | Business rules in API layer                      | Move to domain services/entities                     |
+--------------------------------+--------------------------------------------------+------------------------------------------------------+
| Repository in Domain Services  | Domain depending on infrastructure               | Inject repository interface                          |
+--------------------------------+--------------------------------------------------+------------------------------------------------------+
| Mutable Value Objects          | Value objects that can change                    | Make them immutable (frozen)                         |
+--------------------------------+--------------------------------------------------+------------------------------------------------------+
| Large Aggregates               | Aggregate with 100+ entities                     | Split into separate aggregates                       |
+--------------------------------+--------------------------------------------------+------------------------------------------------------+
| Cross-Aggregate Transactions   | Modifying multiple aggregates in one transaction | Use eventual consistency + events                    |
+--------------------------------+--------------------------------------------------+------------------------------------------------------+

----

Further Reading
===============

- **Book**: "Domain-Driven Design" by Eric Evans (Blue Book)
- **Book**: "Implementing Domain-Driven Design" by Vaughn Vernon (Red Book)
- **Book**: "Domain-Driven Design Distilled" by Vaughn Vernon (Quick intro)