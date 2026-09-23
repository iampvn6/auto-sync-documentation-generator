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

### `delete_user`


```python
delete_user(user_id: int) -> bool
```

Delete a user account.

### `list_users`

@cached<br>

```python
list_users(self, limit: int = 10) -> list[dict]
```

List user accounts.

<!-- DOCSYNC:END -->