# Appendix E: Troubleshooting Guide
## Common Issues and Step-by-Step Solutions

*"Every hive faces challenges on its journey to health. The key is not to avoid problems, but to diagnose and heal them quickly."* - The Debugging Beekeeper

---

## Table of Contents

1. [Quick Problem Diagnosis](#quick-problem-diagnosis)
2. [Sacred Codon Violations](#sacred-codon-violations)
3. [Chemical Toxicity Issues](#chemical-toxicity-issues)
4. [Performance Problems](#performance-problems)
5. [Integration Challenges](#integration-challenges)
6. [Deployment and Runtime Issues](#deployment-and-runtime-issues)
7. [Genesis Engine Problems](#genesis-engine-problems)
8. [Event Sourcing Issues](#event-sourcing-issues)
9. [Team and Process Issues](#team-and-process-issues)
10. [Emergency Response Procedures](#emergency-response-procedures)
11. [Prevention Strategies](#prevention-strategies)
12. [Diagnostic Tools and Commands](#diagnostic-tools-and-commands)

---

## Quick Problem Diagnosis

### Hive Health Check Command

```bash
# Run comprehensive health check
genesis validate --all --detailed --report=health_check.json

# Quick chemical analysis
genesis analyze bonds --detect-toxicity --urgent-only

# Performance snapshot
genesis profile codons --duration=30s --aggregates-only
```

### Symptom-Based Quick Diagnosis

| Symptom | Likely Cause | Quick Fix | Detailed Section |
|---------|--------------|-----------|------------------|
| Slow response times | Chemical toxicity or performance issues | `genesis optimize bonds --auto-fix` | [Performance Problems](#performance-problems) |
| Build failures | Sacred Codon violations | `genesis validate --rules=sacred-codons --fix` | [Sacred Codon Violations](#sacred-codon-violations) |
| Circular dependencies | Chemical bond toxicity | `genesis analyze bonds --break-cycles` | [Chemical Toxicity Issues](#chemical-toxicity-issues) |
| Event processing errors | Event sourcing configuration | Check event store configuration | [Event Sourcing Issues](#event-sourcing-issues) |
| Genesis CLI errors | Installation or configuration | `genesis config reset --reinstall` | [Genesis Engine Problems](#genesis-engine-problems) |

---

## Sacred Codon Violations

### Issue 1: Invalid C→A→G Pattern Implementation

**Symptoms:**
- `SacredCodonViolationException` during command processing
- Events not being generated properly
- State changes without corresponding events

**Diagnosis:**
```bash
genesis validate --component=OrderAggregate --rules=cag-pattern --verbose
```

**Example Violation:**
```python
# WRONG: Direct state mutation bypassing Genesis Events
class OrderAggregate:
    def place_order(self, command):
        self.status = "placed"  # ❌ Direct mutation
        self.total = command.amount
        return None  # ❌ No events generated

# CORRECT: Sacred C→A→G implementation
class OrderAggregate(SacredAggregate):
    def _execute_command_logic(self, command: SacredCommand) -> List[PollenEnvelope]:
        # A: Business logic validation
        if not command.payload.get("items"):
            raise ValueError("Order must contain items")
        
        # State change preparation (no direct mutation yet)
        new_status = "placed"
        total_amount = self._calculate_total(command.payload["items"])
        
        # G: Generate Genesis Events first
        events = [
            self._create_event("OrderPlacedEvent", {
                "order_id": self.id,
                "status": new_status,
                "total": total_amount,
                "items": command.payload["items"]
            })
        ]
        
        return events
    
    def _apply_event(self, event: PollenEnvelope):
        # State changes only through event application
        if event.event_type == "OrderPlacedEvent":
            self.status = event.payload["status"]
            self.total = event.payload["total"]
```

**Step-by-Step Fix:**

1. **Identify the violation:**
```bash
genesis validate --component=OrderAggregate --rules=sacred-codons --output=violations.json
```

2. **Review violation details:**
```json
{
  "component": "OrderAggregate", 
  "violation": "direct_state_mutation",
  "description": "State changed without generating Genesis Event",
  "location": "place_order method line 23",
  "severity": "high"
}
```

3. **Apply the fix:**
```python
# Use Genesis Engine to generate correct pattern
genesis generate fix-violation \
  --component=OrderAggregate \
  --violation=direct_state_mutation \
  --pattern=cag
```

4. **Verify the fix:**
```bash
genesis validate --component=OrderAggregate --rules=sacred-codons
# Expected: ✅ All Sacred Codon patterns validated successfully
```

### Issue 2: Query Side Effects in C→T→C Pattern

**Symptoms:**
- Database writes during query operations
- State changes in read-only methods
- Cache invalidation during queries

**Diagnosis:**
```bash
genesis analyze --component=ProductQuery --pattern=ctc --side-effects
```

**Example Violation:**
```python
# WRONG: Side effects in query
class ProductQueryService:
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        product = self.repository.get_product(product_id)
        
        # ❌ Side effect: updating last accessed time
        product.last_accessed = datetime.now()
        self.repository.save(product)
        
        # ❌ Side effect: cache invalidation
        self.cache.invalidate(f"product_{product_id}")
        
        return product.to_dict()

# CORRECT: Pure C→T→C implementation
class ProductQueryService:
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        # C: Input validation and transformation
        validated_id = self._validate_product_id(product_id)
        
        # T: Pure transformation - no side effects
        raw_product = self.repository.get_product(validated_id)  # Read-only
        enhanced_product = self._enrich_product_data(raw_product)  # Pure function
        
        # C: Output formatting
        return self._format_for_api(enhanced_product)
    
    def _enrich_product_data(self, product: Product) -> EnrichedProduct:
        # Pure function - no side effects
        return EnrichedProduct(
            product=product,
            calculated_discount=self._calculate_discount(product.price),
            availability_status=self._calculate_availability(product.stock)
        )
```

**Step-by-Step Fix:**

1. **Detect side effects:**
```bash
genesis analyze side-effects --component=ProductQueryService --pattern=ctc
```

2. **Review detected side effects:**
```
Side Effects Detected:
❌ Database write operation in query method
❌ Cache invalidation during read operation  
❌ External API call with state modification
```

3. **Remove side effects:**
```python
# Generate pure query implementation
genesis generate query --component=ProductQuery --pure --no-side-effects
```

4. **If tracking needed, use separate command:**
```python
# Separate command for tracking (C→A→G pattern)
class ProductAccessTracker(SacredAggregate):
    def track_product_access(self, command: TrackAccessCommand):
        return [self._create_event("ProductAccessedEvent", {
            "product_id": command.product_id,
            "user_id": command.user_id,
            "timestamp": datetime.now().isoformat()
        })]
```

### Issue 3: Missing Event Correlation in G→C→A→G

**Symptoms:**
- Lost message context in event reactions
- Difficulty tracing event chains
- Broken saga compensations

**Diagnosis:**
```bash
genesis analyze correlation --component=OrderFulfillment --pattern=gcag
```

**Example Problem:**
```python
# WRONG: No event correlation
class InventoryService:
    @EventHandler
    def handle_order_placed(self, event: OrderPlacedEvent):
        # ❌ Lost correlation to original order
        inventory_command = ReserveInventoryCommand(
            items=event.items
            # Missing: original_event_id, correlation_id
        )
        return self.inventory_aggregate.handle_command(inventory_command)

# CORRECT: Proper event correlation
class InventoryService:
    @EventHandler  
    def handle_order_placed(self, event: OrderPlacedEvent):
        # ✅ Maintain event correlation
        inventory_command = create_sacred_command(
            command_type="reserve_inventory",
            payload={
                "items": event.items,
                "order_id": event.order_id,
                "original_event_id": event.event_id,  # Correlation
                "correlation_id": event.correlation_id or event.aggregate_id,
                "causation_id": event.event_id  # What caused this command
            },
            codon_type=SacredCodonType.REACT_TO_EVENT,
            source=f"order_reaction_{event.event_id}"
        )
        
        return self.inventory_aggregate.execute_react_to_event_codon(event)
```

**Step-by-Step Fix:**

1. **Check correlation compliance:**
```bash
genesis validate --component=InventoryService --rules=event-correlation
```

2. **Add correlation metadata:**
```python
# Generate correlation-compliant handler
genesis generate event-handler \
  --source-event=OrderPlacedEvent \
  --target-aggregate=InventoryAggregate \
  --correlation-enabled
```

3. **Verify correlation chain:**
```bash
genesis trace events --correlation-id=order_12345 --depth=5
```

---

## Chemical Toxicity Issues

### Issue 4: Circular Dependency Toxicity

**Symptoms:**
- Build order dependencies
- Runtime initialization failures  
- Difficult unit testing
- Deployment issues

**Diagnosis:**
```bash
genesis analyze bonds --detect-toxicity --type=circular-dependencies
```

**Example Circular Dependency:**
```python
# TOXIC: Circular dependency
class OrderService:
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service
    
    def process_order(self, order):
        payment_result = self.payment_service.process_payment(order)
        return payment_result

class PaymentService:  
    def __init__(self, order_service: OrderService):  # ❌ Circular dependency
        self.order_service = order_service
    
    def process_payment(self, order):
        order_status = self.order_service.get_order_status(order.id)  # ❌ Circular call
        return self._charge_payment(order, order_status)
```

**Chemical Analysis:**
```bash
genesis analyze bonds --component=OrderService,PaymentService --toxicity-report
```

**Output:**
```
🧪 Chemical Toxicity Analysis
═══════════════════════════════════════

Toxic Compound Detected: Circular Dependency Cycle
Components: OrderService ↔ PaymentService
Bond Type: Strong Covalent (High Toxicity)
Toxicity Level: 0.89 (Critical)
Chemical Analogy: Benzene ring causing system instability

Symptoms:
- Compilation order conflicts
- Runtime initialization deadlock
- Testing isolation impossible
- Deployment dependency issues

Recommended Treatment:
1. Dependency Inversion Principle
2. Event-driven decoupling  
3. Extract shared abstraction
4. Use mediator pattern
```

**Step-by-Step Detoxification:**

1. **Break the cycle with Dependency Inversion:**
```python
# ✅ DETOXIFIED: Using abstraction
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, order_data: dict) -> PaymentResult:
        pass

class OrderService:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor
    
    def process_order(self, order):
        # No direct dependency on PaymentService
        payment_data = {
            "order_id": order.id,
            "amount": order.total,
            "currency": order.currency
        }
        payment_result = self.payment_processor.process_payment(payment_data)
        return payment_result

class PaymentService(PaymentProcessor):
    def __init__(self):  # ✅ No circular dependency
        pass
    
    def process_payment(self, order_data: dict) -> PaymentResult:
        # Use event sourcing to get order status if needed
        order_status = self._query_order_status(order_data["order_id"])
        return self._charge_payment(order_data, order_status)
```

2. **Alternative: Event-driven decoupling:**
```python
# ✅ DETOXIFIED: Event-driven approach
class OrderService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    def process_order(self, order):
        # Publish event instead of direct call
        self.event_bus.publish(OrderCreatedEvent(order.to_dict()))
        return ProcessingResult(status="initiated", order_id=order.id)

class PaymentService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe("OrderCreatedEvent", self.handle_order_created)
    
    @SacredCodon(pattern=CodonPattern.REACT_TO_EVENT)
    def handle_order_created(self, event: OrderCreatedEvent):
        # React to event without direct dependency
        payment_result = self._process_payment(event.order_data)
        
        # Publish result event
        if payment_result.success:
            self.event_bus.publish(PaymentCompletedEvent(event.order_id, payment_result))
        else:
            self.event_bus.publish(PaymentFailedEvent(event.order_id, payment_result.error))
```

3. **Apply the fix:**
```bash
genesis refactor break-circular-dependency \
  --components=OrderService,PaymentService \
  --strategy=event-driven
```

4. **Verify detoxification:**
```bash
genesis analyze bonds --components=OrderService,PaymentService --verify-fix
# Expected: ✅ No circular dependencies detected
```

### Issue 5: God Object Chemical Compound

**Symptoms:**
- Single class with excessive responsibilities
- Difficult to test and modify
- High coupling with many other components
- Performance bottlenecks

**Diagnosis:**
```bash
genesis analyze complexity --component=OrderManager --god-object-detection
```

**Example God Object:**
```python
# TOXIC: God Object compound
class OrderManager:  # ❌ 2000+ lines, 50+ methods, 20+ dependencies
    
    def __init__(self, db, payment_gateway, email_service, inventory_service, 
                 shipping_service, tax_calculator, discount_engine, audit_logger,
                 notification_service, analytics_tracker, fraud_detector,
                 customer_service, product_service, warehouse_service):
        # ❌ Too many dependencies - chemical instability
        pass
    
    # ❌ Mixing multiple responsibilities
    def process_order(self, order_data):
        # Order validation
        self._validate_order(order_data)
        
        # Customer management  
        customer = self._get_or_create_customer(order_data['customer'])
        
        # Inventory management
        self._reserve_inventory(order_data['items'])
        
        # Payment processing
        payment_result = self._process_payment(order_data['payment'])
        
        # Tax calculation
        taxes = self._calculate_taxes(order_data)
        
        # Discount calculation
        discounts = self._calculate_discounts(order_data, customer)
        
        # Shipping arrangement
        shipping = self._arrange_shipping(order_data['shipping'])
        
        # Email notifications
        self._send_confirmation_email(customer, order_data)
        
        # Audit logging
        self._log_audit_trail(order_data, payment_result)
        
        # Analytics tracking
        self._track_analytics(order_data, customer)
        
        # Fraud detection
        self._check_fraud(order_data, customer, payment_result)
        
        # And many more responsibilities...
```

**Chemical Analysis:**
```bash
genesis analyze complexity --component=OrderManager --chemical-breakdown
```

**Output:**
```
🧪 Chemical Complexity Analysis
═══════════════════════════════════════

God Object Compound Detected: OrderManager
Molecular Formula: C₁₅H₅₀O₂₀N₁₀ (Unstable oversized molecule)
Molecular Weight: 2847 (Extremely heavy)
Bond Strain: Critical (0.93)
Stability: Very Low (0.12)

Responsibilities Detected: 15
Methods: 52
Lines of Code: 2,134
Dependencies: 18
Chemical Analogy: Oversized carbon molecule causing system instability

Decomposition Recommendations:
1. Extract OrderValidationService
2. Extract PaymentProcessingService  
3. Extract NotificationService
4. Extract AuditingService
5. Use OrderProcessingChoreography for coordination
```

**Step-by-Step Decomposition:**

1. **Extract focused aggregates:**
```python
# ✅ DETOXIFIED: Decomposed into focused aggregates

# Order Management - Core business logic only
@HiveAggregate(domain="order_management")
class OrderAggregate(SacredAggregate):
    def _execute_command_logic(self, command: SacredCommand) -> List[PollenEnvelope]:
        if command.command_type == "create_order":
            return self._create_order(command)
        elif command.command_type == "update_order":
            return self._update_order(command)
        # Only order-specific logic here
    
    def _create_order(self, command: SacredCommand) -> List[PollenEnvelope]:
        # Focus only on order creation logic
        order_data = command.payload
        
        # Basic validation
        self._validate_order_data(order_data)
        
        # Create order entity
        order = Order.from_command(command)
        
        # Generate focused events
        return [
            self._create_event("OrderCreatedEvent", {
                "order_id": order.id,
                "customer_id": order.customer_id,
                "items": order.items,
                "total": order.total
            })
        ]

# Payment Processing - Separate aggregate
@HiveAggregate(domain="payment_processing")  
class PaymentAggregate(SacredAggregate):
    @EventHandler
    @SacredCodon(pattern=CodonPattern.REACT_TO_EVENT)
    def handle_order_created(self, event: OrderCreatedEvent):
        # React to order creation
        payment_command = create_sacred_command(
            command_type="process_payment",
            payload={"order_id": event.order_id, "amount": event.total},
            codon_type=SacredCodonType.HANDLE_COMMAND
        )
        return self.execute_handle_command_codon(payment_command)

# Notification Service - Separate aggregate  
@HiveAggregate(domain="notifications")
class NotificationAggregate(SacredAggregate):
    @EventHandler
    @SacredCodon(pattern=CodonPattern.REACT_TO_EVENT)
    def handle_order_created(self, event: OrderCreatedEvent):
        # Send order confirmation
        notification_command = create_sacred_command(
            command_type="send_order_confirmation",
            payload={"order_id": event.order_id, "customer_id": event.customer_id},
            codon_type=SacredCodonType.HANDLE_COMMAND
        )
        return self.execute_handle_command_codon(notification_command)
```

2. **Coordinate with choreography:**
```python
# ✅ Use choreography for coordination
@Component
class OrderProcessingChoreography:
    @SacredCodon(pattern=CodonPattern.CHOREOGRAPHY)
    def execute_order_processing(self, create_order_command):
        workflow = ChoreographyDefinition.builder()
            .workflowType("order_processing")
            .steps([
                # Step 1: Create order
                ChoreographyStep.builder()
                    .stepId("create_order")
                    .pattern(CodonPattern.HANDLE_COMMAND)
                    .component("OrderAggregate")
                    .build(),
                
                # Step 2: Process payment (triggered by OrderCreated)
                ChoreographyStep.builder()
                    .stepId("process_payment")
                    .pattern(CodonPattern.REACT_TO_EVENT)
                    .triggerEvent("OrderCreatedEvent")
                    .component("PaymentAggregate")
                    .build(),
                
                # Step 3: Send notification (parallel)
                ChoreographyStep.builder()
                    .stepId("send_notification")
                    .pattern(CodonPattern.REACT_TO_EVENT)
                    .triggerEvent("OrderCreatedEvent")
                    .component("NotificationAggregate")
                    .executionMode("PARALLEL")
                    .build()
            ])
            .build()
        
        return self.choreography_engine.execute(workflow)
```

3. **Apply decomposition:**
```bash
genesis refactor decompose-god-object \
  --component=OrderManager \
  --strategy=domain-aggregates \
  --choreography=order-processing
```

4. **Verify decomposition:**
```bash
genesis analyze complexity --all --threshold=moderate
# Expected: ✅ All components within acceptable complexity bounds
```

---

## Performance Problems

### Issue 6: Slow Sacred Codon Execution

**Symptoms:**
- High latency in C→A→G pattern execution
- Event processing delays
- Database connection timeouts
- Memory leaks

**Diagnosis:**
```bash
genesis profile codons --duration=60s --slow-threshold=100ms --detailed
```

**Performance Analysis Output:**
```
🚀 Sacred Codon Performance Analysis
═══════════════════════════════════════

Slow Codon Executions Detected:

❌ OrderAggregate.createOrder (C→A→G)
   Average: 450ms (Target: <50ms)  
   P95: 1.2s
   Bottleneck: Database query in business logic

❌ InventoryService.checkAvailability (C→T→C)
   Average: 280ms (Target: <20ms)
   P95: 890ms  
   Bottleneck: N+1 query problem

❌ PaymentService.processPayment (G→C→A→G)
   Average: 2.1s (Target: <200ms)
   P95: 5.4s
   Bottleneck: Synchronous external API call
```

**Step-by-Step Performance Optimization:**

1. **Identify bottlenecks in C→A→G pattern:**
```python
# SLOW: Database queries in business logic
class OrderAggregate(SacredAggregate):
    def _execute_command_logic(self, command: SacredCommand) -> List[PollenEnvelope]:
        order_data = command.payload
        
        # ❌ Slow: Multiple database calls during command processing
        customer = self.customer_repository.find_by_id(order_data["customer_id"])
        for item in order_data["items"]:
            product = self.product_repository.find_by_id(item["product_id"])  # N+1 problem
            inventory = self.inventory_repository.check_stock(item["product_id"])
        
        # Business logic continues...

# FAST: Optimized with batch loading and caching
class OrderAggregate(SacredAggregate):
    def _execute_command_logic(self, command: SacredCommand) -> List[PollenEnvelope]:
        order_data = command.payload
        
        # ✅ Fast: Batch load all required data upfront
        product_ids = [item["product_id"] for item in order_data["items"]]
        
        # Single batch query instead of N+1
        products = self.product_repository.find_by_ids(product_ids)  
        inventory_levels = self.inventory_repository.check_stock_batch(product_ids)
        
        # Cache customer data
        customer = self._get_cached_customer(order_data["customer_id"])
        
        # Now process business logic with pre-loaded data
        return self._process_order_with_data(order_data, customer, products, inventory_levels)
    
    @cached(ttl=300)  # 5-minute cache
    def _get_cached_customer(self, customer_id: str) -> Customer:
        return self.customer_repository.find_by_id(customer_id)
```

2. **Optimize C→T→C pattern for queries:**
```python
# SLOW: Individual queries
class InventoryQueryService:
    def check_availability(self, product_ids: List[str]) -> Dict[str, int]:
        availability = {}
        for product_id in product_ids:  # ❌ N+1 problem
            stock_level = self.inventory_repository.get_stock_level(product_id)
            availability[product_id] = stock_level
        return availability

# FAST: Batch queries and caching  
class OptimizedInventoryQueryService:
    def __init__(self):
        self.redis_cache = redis.Redis()
    
    def check_availability(self, product_ids: List[str]) -> Dict[str, int]:
        # Check cache first
        cached_availability = self._get_cached_availability(product_ids)
        missing_ids = [pid for pid in product_ids if pid not in cached_availability]
        
        if missing_ids:
            # Single batch query for missing items
            fresh_availability = self.inventory_repository.get_stock_levels_batch(missing_ids)
            
            # Cache results
            self._cache_availability(fresh_availability)
            
            # Merge cached and fresh data
            cached_availability.update(fresh_availability)
        
        return cached_availability
    
    def _get_cached_availability(self, product_ids: List[str]) -> Dict[str, int]:
        pipe = self.redis_cache.pipeline()
        for pid in product_ids:
            pipe.get(f"inventory:{pid}")
        
        results = pipe.execute()
        
        availability = {}
        for pid, result in zip(product_ids, results):
            if result is not None:
                availability[pid] = int(result)
        
        return availability
```

3. **Optimize G→C→A→G pattern with async processing:**
```python
# SLOW: Synchronous external calls
class PaymentService:
    @SacredCodon(pattern=CodonPattern.REACT_TO_EVENT)
    def handle_payment_request(self, event: PaymentRequestEvent):
        # ❌ Blocking call to payment gateway
        payment_result = self.payment_gateway.charge_card(
            event.card_info, event.amount
        )  # Takes 2+ seconds
        
        return [PaymentProcessedEvent(payment_result)]

# FAST: Async processing with timeouts
class OptimizedPaymentService:
    @SacredCodon(pattern=CodonPattern.REACT_TO_EVENT)
    async def handle_payment_request(self, event: PaymentRequestEvent):
        try:
            # ✅ Async with timeout and circuit breaker
            payment_result = await asyncio.wait_for(
                self.payment_gateway.charge_card_async(
                    event.card_info, event.amount
                ),
                timeout=5.0  # 5-second timeout
            )
            
            return [PaymentProcessedEvent(payment_result)]
            
        except asyncio.TimeoutError:
            # Handle timeout gracefully
            return [PaymentTimeoutEvent(event.payment_id, "Gateway timeout")]
        
        except PaymentGatewayException as e:
            # Handle gateway errors
            return [PaymentFailedEvent(event.payment_id, str(e))]
```

4. **Apply performance optimizations:**
```bash
genesis optimize performance \
  --component=OrderAggregate,InventoryService,PaymentService \
  --strategy=caching,batching,async
```

5. **Verify improvements:**
```bash
genesis profile codons --duration=60s --compare=baseline
```

**Expected Results:**
```
🚀 Performance Improvement Results
═══════════════════════════════════════

OrderAggregate.createOrder (C→A→G)
Before: 450ms → After: 45ms (90% improvement) ✅

InventoryService.checkAvailability (C→T→C)  
Before: 280ms → After: 18ms (94% improvement) ✅

PaymentService.processPayment (G→C→A→G)
Before: 2.1s → After: 180ms (91% improvement) ✅

Overall System Performance: 92% improvement
```

### Issue 7: Memory Leaks in Event Processing

**Symptoms:**
- Gradual memory increase over time
- OutOfMemoryError in production
- Slow garbage collection
- Event queue buildup

**Diagnosis:**
```bash
genesis profile memory --component=EventProcessor --leak-detection
```

**Example Memory Leak:**
```python
# MEMORY LEAK: Event handlers keeping references
class LeakyEventProcessor:
    def __init__(self):
        self.processed_events = []  # ❌ Growing list never cleared
        self.event_handlers = {}
    
    def process_event(self, event: PollenEnvelope):
        # ❌ Memory leak: keeping all processed events in memory
        self.processed_events.append(event)
        
        # ❌ Memory leak: lambda captures entire event object
        handler = lambda: self._handle_with_context(event)  
        self.event_handlers[event.event_id] = handler
        
        result = handler()
        
        # ❌ Never cleanup handlers dictionary
        return result

# MEMORY EFFICIENT: Proper cleanup and weak references
import weakref
from collections import deque

class EfficientEventProcessor:
    def __init__(self):
        # ✅ Use bounded deque for recent events only
        self.recent_events = deque(maxlen=1000)  
        
        # ✅ Use weak references for handlers
        self.event_handlers = weakref.WeakValueDictionary()
        
        # ✅ Track memory usage
        self.processed_count = 0
        self.cleanup_threshold = 10000
    
    def process_event(self, event: PollenEnvelope):
        # ✅ Add to bounded collection
        self.recent_events.append(event.event_id)  # Store ID only, not full event
        
        # ✅ Process without keeping references
        result = self._handle_event(event)
        
        # ✅ Periodic cleanup
        self.processed_count += 1
        if self.processed_count % self.cleanup_threshold == 0:
            self._cleanup_memory()
        
        return result
    
    def _cleanup_memory(self):
        # ✅ Explicit memory cleanup
        import gc
        gc.collect()
        
        # ✅ Clear old handler references
        self.event_handlers.clear()
        
        logger.info(f"Memory cleanup completed. Processed {self.processed_count} events.")
```

**Step-by-Step Memory Optimization:**

1. **Identify memory leaks:**
```bash
genesis analyze memory-leaks --component=EventProcessor --duration=1h
```

2. **Apply memory-efficient patterns:**
```bash
genesis optimize memory \
  --component=EventProcessor \
  --strategy=weak-references,bounded-collections,periodic-cleanup
```

3. **Monitor memory usage:**
```bash
genesis monitor memory --component=EventProcessor --alert-threshold=80%
```

---

## Integration Challenges

### Issue 8: Legacy System Integration Failures

**Symptoms:**
- Timeouts connecting to legacy systems
- Data format mismatches
- Authentication failures
- Transaction rollback issues

**Diagnosis:**
```bash
genesis diagnose integration --legacy-system=MainframeOrderSystem --verbose
```

**Example Integration Problem:**
```python
# FRAGILE: Direct legacy integration
class OrderService:
    def process_order(self, order):
        try:
            # ❌ Direct coupling to legacy system
            mainframe_request = self._convert_to_mainframe_format(order)
            response = self.mainframe_client.submit_order(mainframe_request)
            
            if response.status_code != 200:
                raise IntegrationError("Mainframe rejected order")
                
            return response
            
        except ConnectionTimeout:
            # ❌ Poor error handling
            raise SystemError("Mainframe unavailable")

# RESILIENT: Adapter pattern with circuit breaker
class ResilientOrderService:
    def __init__(self):
        self.mainframe_adapter = MainframeAdapter()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=IntegrationException
        )
        self.fallback_processor = FallbackOrderProcessor()
    
    @SacredCodon(pattern=CodonPattern.HANDLE_COMMAND)
    def process_order(self, command: SacredCommand) -> List[PollenEnvelope]:
        order_data = command.payload
        
        try:
            # ✅ Use circuit breaker for resilience
            mainframe_result = self.circuit_breaker.call(
                self._process_with_mainframe, order_data
            )
            
            return [OrderProcessedEvent(order_data["order_id"], mainframe_result)]
            
        except CircuitBreakerOpenException:
            # ✅ Graceful degradation
            logger.warning("Mainframe circuit breaker open, using fallback")
            fallback_result = self.fallback_processor.process_order(order_data)
            
            return [
                OrderProcessedEvent(order_data["order_id"], fallback_result),
                MainframeUnavailableEvent(order_data["order_id"], "circuit_breaker_open")
            ]
    
    def _process_with_mainframe(self, order_data):
        # ✅ Adapter handles format conversion and retries
        return self.mainframe_adapter.submit_order(order_data)

class MainframeAdapter:
    def __init__(self):
        self.retry_policy = RetryPolicy(
            max_attempts=3,
            backoff_strategy=ExponentialBackoff(base_delay=1.0, max_delay=10.0)
        )
    
    @HiveConnector(type="SECONDARY", protocol="MQ_SERIES")
    def submit_order(self, order_data):
        # ✅ Format conversion with validation
        mainframe_format = self._convert_to_mainframe_format(order_data)
        self._validate_mainframe_format(mainframe_format)
        
        # ✅ Retry with exponential backoff
        return self.retry_policy.execute(
            lambda: self._send_to_mainframe(mainframe_format)
        )
```

**Step-by-Step Integration Fix:**

1. **Analyze integration points:**
```bash
genesis analyze integrations --legacy-systems --resilience-report
```

2. **Generate resilient adapters:**
```bash
genesis generate adapter \
  --legacy-system=MainframeOrderSystem \
  --resilience=circuit-breaker,retry,fallback
```

3. **Test integration resilience:**
```bash
genesis test integration --chaos-engineering --failure-scenarios
```

### Issue 9: API Version Compatibility Issues

**Symptoms:**
- Breaking changes in external APIs
- Incompatible response formats
- Authentication token expiration
- Rate limiting errors

**Solution: Versioned API Adapters**

```python
# Resilient API integration with versioning
@HiveConnector(type="SECONDARY", protocol="REST_API")
class VersionedPaymentConnector:
    def __init__(self):
        self.api_versions = {
            "v1": PaymentAPIv1Client(),
            "v2": PaymentAPIv2Client(),
            "v3": PaymentAPIv3Client()
        }
        self.preferred_version = "v3"
        self.fallback_versions = ["v2", "v1"]
    
    @SacredCodon(pattern=CodonPattern.HANDLE_COMMAND)
    def process_payment(self, command: SacredCommand) -> List[PollenEnvelope]:
        payment_data = command.payload
        
        # Try preferred version first
        for version in [self.preferred_version] + self.fallback_versions:
            try:
                api_client = self.api_versions[version]
                result = self._process_with_version(api_client, payment_data, version)
                
                return [PaymentProcessedEvent(payment_data["payment_id"], result)]
                
            except APIVersionDeprecatedException:
                logger.warning(f"Payment API {version} deprecated, trying next version")
                continue
            except APICompatibilityException as e:
                logger.error(f"Payment API {version} compatibility error: {e}")
                continue
        
        # All versions failed
        return [PaymentFailedEvent(
            payment_data["payment_id"], 
            "All API versions failed"
        )]
    
    def _process_with_version(self, api_client, payment_data, version):
        # Version-specific data transformation
        if version == "v3":
            return api_client.charge_card_v3(
                card_token=payment_data["card_token"],
                amount_cents=int(payment_data["amount"] * 100),
                currency=payment_data["currency"]
            )
        elif version == "v2":
            return api_client.charge_card_v2(
                card_number=payment_data["card_number"],
                amount_dollars=payment_data["amount"],
                currency_code=payment_data["currency"]
            )
        else:  # v1
            return api_client.charge_card_v1(
                card_info=payment_data,
                charge_amount=payment_data["amount"]
            )
```

**Step-by-Step API Compatibility Fix:**

1. **Detect API version issues:**
```bash
genesis diagnose api-compatibility --external-apis --version-matrix
```

2. **Generate versioned connectors:**
```bash
genesis generate versioned-connector \
  --api=PaymentGatewayAPI \
  --versions=v1,v2,v3 \
  --fallback-strategy=graceful-degradation
```

3. **Test version compatibility:**
```bash
genesis test api-versions --connector=PaymentConnector --all-versions
```

---

## Deployment and Runtime Issues

### Issue 10: Container Startup Failures

**Symptoms:**
- Pods crashing on Kubernetes
- Database connection failures at startup
- Configuration loading errors
- Health check failures

**Diagnosis:**
```bash
genesis diagnose deployment --environment=kubernetes --component=OrderService
```

**Example Startup Issue:**
```yaml
# PROBLEMATIC: Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: order-service
        image: order-service:latest
        env:
        - name: DATABASE_URL
          value: "postgresql://localhost:5432/orders"  # ❌ Wrong host
        # ❌ Missing readiness/liveness probes
        # ❌ No resource limits
        # ❌ No graceful shutdown configuration
```

**Step-by-Step Deployment Fix:**

1. **Generate proper deployment config:**
```bash
genesis generate deployment kubernetes \
  --component=OrderService \
  --environment=production \
  --health-checks \
  --resource-limits \
  --graceful-shutdown
```

2. **Correct deployment configuration:**
```yaml
# ✅ CORRECTED: Robust Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  labels:
    app: order-service
    version: v1.2.3
    hive.arch/domain: order-management
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
        version: v1.2.3
      annotations:
        hive.arch/sacred-codons: "cag,ctc,gcag"
        hive.arch/chemical-health: "monitored"
    spec:
      containers:
      - name: order-service
        image: order-service:v1.2.3  # ✅ Specific version tag
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 8081
          name: health
        
        # ✅ Proper environment configuration
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: SPRING_PROFILES_ACTIVE
          value: "production,kubernetes"
        - name: GENESIS_ENGINE_ENABLED
          value: "true"
        - name: CHEMICAL_MONITORING_ENABLED
          value: "true"
        
        # ✅ Resource limits
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        
        # ✅ Health checks
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8081
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8081
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # ✅ Graceful shutdown
        lifecycle:
          preStop:
            exec:
              command:
              - /bin/sh
              - -c
              - "sleep 15; kill -SIGTERM 1"
        
        # ✅ Security context
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        
        # ✅ Volume mounts for temporary files
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/cache
      
      # ✅ Volumes
      volumes:
      - name: tmp
        emptyDir: {}
      - name: cache
        emptyDir: {}
      
      # ✅ Pod security
      securityContext:
        fsGroup: 1000
      
      # ✅ Service account
      serviceAccountName: order-service
      
      # ✅ Graceful termination
      terminationGracePeriodSeconds: 30
```

3. **Add health check endpoints:**
```java
@RestController
@RequestMapping("/actuator/health")
public class HiveHealthController {
    
    @Autowired
    private ChemicalHealthMonitor chemicalHealth;
    
    @Autowired
    private DatabaseHealthIndicator dbHealth;
    
    @GetMapping("/liveness")
    public ResponseEntity<Map<String, Object>> liveness() {
        // Basic liveness check
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("timestamp", Instant.now());
        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/readiness")
    public ResponseEntity<Map<String, Object>> readiness() {
        Map<String, Object> response = new HashMap<>();
        
        // Check database connectivity
        boolean dbHealthy = dbHealth.isHealthy();
        
        // Check chemical health
        ChemicalHealthStatus chemicalStatus = chemicalHealth.getCurrentHealth();
        boolean chemicallyHealthy = chemicalStatus.getOverallHealth() > 0.7;
        
        // Check Sacred Codon compliance
        boolean codonsHealthy = chemicalStatus.getSacredCodonCompliance() > 0.9;
        
        boolean ready = dbHealthy && chemicallyHealthy && codonsHealthy;
        
        response.put("status", ready ? "UP" : "DOWN");
        response.put("database", dbHealthy ? "UP" : "DOWN");
        response.put("chemical_health", chemicalStatus.getOverallHealth());
        response.put("sacred_codon_compliance", chemicalStatus.getSacredCodonCompliance());
        response.put("timestamp", Instant.now());
        
        return ResponseEntity.status(ready ? 200 : 503).body(response);
    }
}
```

4. **Verify deployment:**
```bash
genesis validate deployment --environment=kubernetes --health-checks
```

---

## Genesis Engine Problems

### Issue 11: Genesis Engine Installation Issues

**Symptoms:**
- `genesis command not found`
- Permission errors during installation
- Version compatibility issues
- Template generation failures

**Step-by-Step Installation Fix:**

1. **Verify installation:**
```bash
# Check if Genesis Engine is installed
which genesis

# Check version
genesis --version

# Verify installation health
genesis validate --self-test
```

2. **Clean installation:**
```bash
# Remove existing installation
npm uninstall -g @hive-arch/genesis-engine

# Clear npm cache
npm cache clean --force

# Reinstall with proper permissions
sudo npm install -g @hive-arch/genesis-engine

# Verify installation
genesis --version
genesis validate --self-test
```

3. **Fix permissions (Linux/Mac):**
```bash
# Create npm global directory with proper permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH=~/.npm-global/bin:$PATH

# Reinstall without sudo
npm install -g @hive-arch/genesis-engine
```

4. **Alternative: Local installation:**
```bash
# Install locally in project
npm install @hive-arch/genesis-engine

# Use with npx
npx genesis --version
```

### Issue 12: Template Generation Failures

**Symptoms:**
- `genesis hatch` command fails
- Template files not found
- Incomplete component generation
- Template variable substitution errors

**Diagnosis:**
```bash
genesis diagnose templates --verbose --component-type=aggregate
```

**Step-by-Step Template Fix:**

1. **Verify template installation:**
```bash
genesis list templates --all --detailed
```

2. **Reinstall templates:**
```bash
genesis install templates --all --force-update
```

3. **Fix custom template:**
```bash
# If using custom templates, verify structure
genesis validate template --template-path=./custom-templates/aggregate
```

4. **Generate with debugging:**
```bash
genesis hatch aggregate OrderTest --debug --verbose --dry-run
```

---

## Event Sourcing Issues

### Issue 13: Event Store Corruption

**Symptoms:**
- Event deserialization errors
- Missing events in event stream
- Aggregate rehydration failures
- Event ordering inconsistencies

**Diagnosis:**
```bash
genesis diagnose event-store --corruption-check --aggregate=OrderAggregate
```

**Step-by-Step Event Store Recovery:**

1. **Check event store integrity:**
```python
# Event store health check
class EventStoreHealthChecker:
    def check_integrity(self, aggregate_id: str) -> IntegrityReport:
        events = self.event_store.get_events(aggregate_id)
        
        issues = []
        
        # Check event sequence
        expected_version = 1
        for event in events:
            if event.version != expected_version:
                issues.append(f"Version gap: expected {expected_version}, got {event.version}")
            expected_version = event.version + 1
        
        # Check event deserialization
        for event in events:
            try:
                deserialized = self.event_serializer.deserialize(event.data)
            except Exception as e:
                issues.append(f"Deserialization error in event {event.id}: {e}")
        
        return IntegrityReport(aggregate_id, issues)
```

2. **Repair corrupted events:**
```bash
genesis repair event-store \
  --aggregate=OrderAggregate \
  --fix-sequence-gaps \
  --fix-serialization-errors \
  --backup-first
```

3. **Prevent future corruption:**
```python
# Add event validation
class ValidatingEventStore:
    def append_event(self, aggregate_id: str, event: PollenEnvelope):
        # Validate event before storage
        validation_result = self._validate_event(event)
        if not validation_result.is_valid:
            raise InvalidEventException(f"Event validation failed: {validation_result.errors}")
        
        # Check sequence consistency
        last_version = self._get_last_version(aggregate_id)
        if event.version != last_version + 1:
            raise EventSequenceException(f"Expected version {last_version + 1}, got {event.version}")
        
        # Store with checksum
        event_data = self._serialize_with_checksum(event)
        self._store_event(aggregate_id, event_data)
    
    def _serialize_with_checksum(self, event: PollenEnvelope) -> bytes:
        serialized = self.serializer.serialize(event)
        checksum = hashlib.sha256(serialized).hexdigest()
        
        return {
            'data': serialized,
            'checksum': checksum,
            'timestamp': datetime.utcnow().isoformat()
        }
```

---

## Emergency Response Procedures

### Production Incident Response

When a production Hive system experiences issues:

#### Immediate Response (0-5 minutes)
```bash
# 1. Check system health
genesis status --environment=production --critical-only

# 2. Identify failing components  
genesis diagnose --production --failing-components

# 3. Check chemical health
genesis analyze bonds --production --toxicity-critical

# 4. Enable emergency mode if needed
genesis emergency-mode enable --reason="production-incident"
```

#### Assessment Phase (5-15 minutes)
```bash
# 5. Generate incident report
genesis incident create \
  --severity=high \
  --affected-components="OrderService,PaymentService" \
  --report-id="INC-$(date +%Y%m%d-%H%M%S)"

# 6. Check recent deployments
genesis deployment history --last=24h --changes-only

# 7. Analyze error patterns
genesis analyze errors --production --last=1h --patterns
```

#### Mitigation Phase (15-60 minutes)
```bash
# 8. Apply emergency fixes
genesis emergency fix-toxicity --auto-approve --components="OrderService"

# 9. Scale resources if needed
genesis scale --component=OrderService --replicas=10 --reason="incident-response"

# 10. Enable circuit breakers
genesis circuit-breaker enable --all-external-deps --timeout=30s
```

#### Recovery Phase (1-4 hours)
```bash
# 11. Monitor recovery
genesis monitor recovery --incident=INC-20241201-143022 --auto-update

# 12. Validate system health
genesis validate --all --production --post-incident-check

# 13. Generate post-incident report
genesis incident report --incident=INC-20241201-143022 --full-analysis
```

### Disaster Recovery

For catastrophic system failures:

1. **Activate Disaster Recovery Plan:**
```bash
genesis disaster-recovery activate \
  --plan=production-dr \
  --failover-region=us-west-2 \
  --confirm-data-loss-acceptable
```

2. **Restore from Backups:**
```bash
genesis restore event-store \
  --from-backup=prod-backup-20241201-000000 \
  --target-environment=dr \
  --validate-integrity
```

3. **Verify System Recovery:**
```bash
genesis validate --environment=dr --full-system-check --compare=production
```

---

## Prevention Strategies

### Continuous Health Monitoring

```yaml
# .github/workflows/hive-health-monitoring.yml
name: Continuous Hive Health Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  push:
    branches: [main]

jobs:
  chemical-health-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Install Genesis Engine
      run: npm install -g @hive-arch/genesis-engine
    
    - name: Run Chemical Health Analysis
      run: |
        genesis analyze bonds --all --toxicity-report --format=json > chemical-health.json
        
        # Check if toxicity is above threshold
        TOXICITY=$(jq '.overall_toxicity' chemical-health.json)
        if (( $(echo "$TOXICITY > 0.3" | bc -l) )); then
          echo "❌ High toxicity detected: $TOXICITY"
          exit 1
        fi
    
    - name: Validate Sacred Codons
      run: genesis validate --rules=sacred-codons --all --strict
    
    - name: Performance Baseline Check
      run: genesis profile codons --baseline=performance-baseline.json --compare
    
    - name: Generate Health Report
      run: |
        genesis report health \
          --format=html \
          --output=hive-health-report.html \
          --include-recommendations
    
    - name: Upload Health Report
      uses: actions/upload-artifact@v3
      with:
        name: hive-health-report
        path: hive-health-report.html
```

### Automated Quality Gates

```python
# quality_gates.py - Automated quality enforcement
class HiveQualityGates:
    def __init__(self):
        self.chemical_health_threshold = 0.8
        self.toxicity_threshold = 0.2
        self.sacred_codon_compliance_threshold = 0.95
    
    def validate_pull_request(self, pr_changes):
        """Validate pull request against Hive quality standards"""
        
        validation_results = []
        
        # 1. Chemical health check
        chemical_health = self.analyze_chemical_health(pr_changes)
        if chemical_health.overall_health < self.chemical_health_threshold:
            validation_results.append(ValidationFailure(
                "Chemical health below threshold",
                f"Current: {chemical_health.overall_health}, Required: {self.chemical_health_threshold}"
            ))
        
        # 2. Toxicity check  
        toxicity = self.detect_toxicity(pr_changes)
        if toxicity.level > self.toxicity_threshold:
            validation_results.append(ValidationFailure(
                "Toxicity level too high",
                f"Current: {toxicity.level}, Threshold: {self.toxicity_threshold}",
                toxicity.violations
            ))
        
        # 3. Sacred Codon compliance
        codon_compliance = self.validate_sacred_codons(pr_changes)
        if codon_compliance.score < self.sacred_codon_compliance_threshold:
            validation_results.append(ValidationFailure(
                "Sacred Codon compliance below threshold",
                f"Current: {codon_compliance.score}, Required: {self.sacred_codon_compliance_threshold}",
                codon_compliance.violations
            ))
        
        return ValidationReport(
            passed=len(validation_results) == 0,
            failures=validation_results
        )
```

### Team Training and Certification

```python
# Hive Architecture Certification Program
class HiveCertificationProgram:
    
    CERTIFICATION_LEVELS = {
        "hive_practitioner": {
            "requirements": [
                "Complete Sacred Codon training",
                "Implement 5 C→A→G patterns",
                "Demonstrate chemical health monitoring",
                "Pass Genesis Engine proficiency test"
            ],
            "duration": "40 hours"
        },
        
        "hive_architect": {
            "requirements": [
                "Hold Hive Practitioner certification",
                "Design and implement choreography patterns",
                "Conduct chemical bond analysis",
                "Lead team transformation project",
                "Pass advanced architecture exam"
            ],
            "duration": "80 hours"
        },
        
        "hive_master": {
            "requirements": [
                "Hold Hive Architect certification", 
                "Contribute to Genesis Engine development",
                "Publish case study or research",
                "Mentor other practitioners",
                "Pass master-level assessment"
            ],
            "duration": "120 hours"
        }
    }
```

---

## Conclusion

This troubleshooting guide provides comprehensive solutions to common issues encountered when implementing Hive Architecture. The key to successful troubleshooting is:

1. **Use Genesis Engine Tools**: Leverage built-in diagnostic capabilities
2. **Monitor Chemical Health**: Continuous monitoring prevents problems
3. **Follow Sacred Patterns**: Violations are the root cause of many issues
4. **Implement Prevention**: Automated quality gates catch issues early
5. **Train Your Team**: Well-trained teams prevent more issues than they fix

### Next Steps

1. **Bookmark this guide** for quick reference during incidents
2. **Set up monitoring** using the provided scripts and configurations
3. **Implement quality gates** in your CI/CD pipeline
4. **Train your team** on common troubleshooting procedures
5. **Contribute back** by reporting new issues and solutions

### Related Resources

- **[Appendix A: Genesis Engine CLI Reference](appendix_a_genesis_engine_cli_reference.md)** - Complete command reference
- **[Appendix C: Chemical Bond Analysis Tools](appendix_c_chemical_bond_analysis_tools.md)** - Analysis techniques
- **[Appendix G: Metrics and Monitoring](appendix_g_metrics_and_monitoring.md)** - Monitoring setup

*"The healthiest hives are not those that never face problems, but those that detect, diagnose, and heal quickly. Build your immune systems strong, and your hive will thrive through any challenge."* - The Master Debugger