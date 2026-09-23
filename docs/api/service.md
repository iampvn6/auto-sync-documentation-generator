# API Reference: `service`

<!-- DOCSYNC:START -->

## Functions

### `cached`


```python
cached(func)
```

Example decorator.

### `require_auth`


```python
require_auth(func)
```

Example decorator.

### `create_user`

@require_auth<br>

```python
create_user(name: str, active: bool = True) -> dict
```

Create a new user account.

<!-- DOCSYNC:END -->