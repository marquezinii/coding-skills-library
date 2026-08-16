# Basic update example

Given an existing `llms.txt`, compare every listed path with the repository and make the smallest accurate update.

```diff
 ## Documentation

 - [README](README.md): Setup and usage.
- - [Old API guide](docs/api-v1.md): Legacy API.
+ - [API guide](docs/api.md): Current API and examples.
```

Remove stale links, preserve useful descriptions, and validate the resulting relative paths.
