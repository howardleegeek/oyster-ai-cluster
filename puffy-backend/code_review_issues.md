# Code Review - Bugs and Issues Found

## Critical Bugs

### 1. Unresolved dependency (app/services/order.py:32)
- **Issue**: `self.wallet_db` is used but never defined in the OrderService `__init__` method
- **Location**: app/services/order.py:25-33
- **Fix**: Add `self.wallet_db = wallet_db` parameter to `__init__`
- **Impact**: Will cause AttributeError at runtime when wallet_db is used

### 2. Undefined type (app/db/__init__.py:4)
- **Issue**: `WalletRepoDep` is referenced but the `Wallet` class doesn't exist in any file
- **Location**: app/db/__init__.py:4
- **Fix**: Create the `Wallet` repository class or remove the unused dependency
- **Impact**: Module import will fail at startup

### 3. Missing Wallet dependency injection (app/services/order.py)
- **Issue**: OrderService expects a `wallet_db` parameter in `get_order_service` (line 161-167) but it's not in the signature
- **Location**: app/services/order.py:161-167
- **Fix**: Add `wallet_db: WalletRepoDep` to the `get_order_service` function signature
- **Impact**: Will cause TypeError at runtime

## Major Issues

### 4. Using deprecated Pydantic method (app/services/product.py:29)
- **Issue**: `from_orm()` is deprecated in Pydantic v2
- **Location**: app/services/product.py:29
- **Fix**: Replace with `model_validate()` or `model_copy()`
- **Impact**: Deprecated API will be removed in future Pydantic versions

### 5. Missing imports (app/services/order.py)
- **Issue**: Uses `InvalidNFTError` and `UnauthorizedError` but they're defined in app/services/error.py
- **Location**: app/services/order.py:16
- **Fix**: Verify the import statement and ensure exceptions are correctly exported
- **Impact**: Potential NameError if exceptions aren't properly exported

### 6. Database initialization order (app/puffy.py:28)
- **Issue**: `Base.metadata.create_all(bind=engine)` is called inside `start_app()` before routers are included
- **Location**: app/puffy.py:28
- **Fix**: Move database initialization before router inclusion
- **Impact**: Tables may not be created in the correct order

### 7. Cache singleton initialization (app/db/cache.py:54)
- **Issue**: `_CACHE_INSTANCE = CacheDb(get_settings())` is called at module level
- **Location**: app/db/cache.py:54
- **Fix**: Initialize cache after settings are loaded or make it lazy
- **Impact**: Settings might not be fully loaded, causing runtime errors

### 8. Currency field mismatch (app/models/order.py:125)
- **Issue**: Uses `mapped_column(DECIMAL(20, 9))` but defined as `Mapped[int]` in Payment schema
- **Location**: app/models/order.py:125
- **Fix**: Match types between model and schema
- **Impact**: Type mismatches can cause runtime errors

## Minor Issues

### 9. Unused imports (app/services/product.py:2)
- **Issue**: `decimal` is imported but never used
- **Location**: app/services/product.py:2
- **Fix**: Remove unused import
- **Impact**: Minimal - code cleanliness

### 10. Unused variables (app/services/product.py:26-28)
- **Issue**: Prints product and type but doesn't use the variables
- **Location**: app/services/product.py:26-28
- **Fix**: Remove debug prints or use the variables
- **Impact**: Minimal - debug noise

### 11. Missing method (app/models/user.py:69)
- **Issue**: `self.balance.get_level()` is called but Balance class doesn't have this method
- **Location**: app/models/user.py:69
- **Fix**: Add `get_level()` method to Balance class or remove the call
- **Impact**: Will cause AttributeError

### 12. Potential None value access (app/db/order.py:90)
- **Issue**: `address_db` could be None if shipping address is loaded with innerjoin=False
- **Location**: app/db/order.py:90
- **Fix**: Add None check before accessing address_db attributes
- **Impact**: Potential AttributeError

### 13. Hardcoded values (app/services/order.py:113-114)
- **Issue**: Shipping fees hardcoded for "CN" and "US"
- **Location**: app/services/order.py:113-114
- **Fix**: Use config or database settings
- **Impact**: Hard to maintain and configure

### 14. JSON serialization issues (app/db/cache.py:27)
- **Issue**: `model_dump_json()` might fail if data contains non-serializable types
- **Location**: app/db/cache.py:27
- **Fix**: Add error handling for serialization
- **Impact**: Potential crashes when session data is invalid

### 15. Race condition in create_user (app/db/user.py:66-69)
- **Issue**: Multiple IntegrityError catches could still have race conditions
- **Location**: app/db/user.py:66-69
- **Fix**: Use a more robust uniqueness check with locking
- **Impact**: Potential duplicate user creation under high concurrency

## Security Concerns

### 16. Token parsing (app/services/token.py:36-37)
- **Issue**: No input validation on token before splitting
- **Location**: app/services/token.py:36-37
- **Fix**: Add token validation before processing
- **Impact**: Could expose sensitive information in logs

### 17. Missing input validation (app/services/order.py:97-103)
- **Issue**: No validation on order items or prices
- **Location**: app/services/order.py:97-103
- **Fix**: Add input validation for all order parameters
- **Impact**: Potential for integer overflow or negative values

### 18. Redis session expiration (app/db/cache.py:27)
- **Issue**: Session expiration is hardcoded to 600 seconds
- **Location**: app/db/cache.py:27
- **Fix**: Make expiration configurable via settings
- **Impact**: Security risk - sessions might expire too early or too late

## Summary

**Total Issues Found**: 18
- Critical: 3
- Major: 5
- Minor: 8
- Security: 2

**Priority**: Address critical and major issues first to prevent runtime errors and security vulnerabilities.
