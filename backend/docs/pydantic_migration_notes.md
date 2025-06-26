# Pydantic V2 Migration Notes

## Overview

The backend currently uses Pydantic V1 style validators and configurations which are deprecated in Pydantic V2. These deprecation warnings do not affect functionality but should be addressed in a future migration.

## Current Deprecation Warnings

### 1. Validator Style
**Current (V1):**
```python
@validator('field_name')
def validate_field(cls, v):
    return v
```

**Should be (V2):**
```python
@field_validator('field_name')
@classmethod
def validate_field(cls, v):
    return v
```

### 2. Config Class
**Current (V1):**
```python
class Config:
    json_encoders = {...}
```

**Should be (V2):**
```python
model_config = ConfigDict(
    json_encoders={...}
)
```

### 3. Field Constraints
**Current (V1):**
```python
Field(..., min_items=1, max_items=10)
```

**Should be (V2):**
```python
Field(..., min_length=1, max_length=10)
```

### 4. Extra Field Arguments
**Current (V1):**
```python
Field(..., env='ENV_VAR')
```

**Should be (V2):**
```python
Field(..., json_schema_extra={'env': 'ENV_VAR'})
```

## Files Affected

- `models/base.py` - Multiple validators and config classes
- `models/job_models.py` - Several validators
- `utils/config.py` - Field with env extra argument

## Suppressing Warnings

Warnings are currently suppressed via:
1. `pytest.ini` configuration
2. Test runner warning filters
3. Command line `-W ignore::DeprecationWarning`

## Migration Strategy

When ready to migrate:
1. Update all validators to V2 style
2. Replace Config classes with ConfigDict
3. Update Field constraints
4. Test thoroughly as behavior may change slightly
5. Remove warning suppressions

## References

- [Pydantic V2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Field Validators Documentation](https://docs.pydantic.dev/latest/concepts/validators/)
- [Model Configuration](https://docs.pydantic.dev/latest/concepts/config/)