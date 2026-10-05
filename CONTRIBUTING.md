# Contributing

Please follow this guide to propose changes so they can be reviewed and merged smoothly.

## Branches

- `main` is the stable branch. **Do not commit directly to it.**
- Create a new branch for each change, using one of these prefixes:
  - `feature/` for new exercises or pages (e.g. `feature/tema-2-exercises`)
  - `fix/` for corrections (e.g. `fix/broken-image-path`)
  - `docs/` for documentation changes (e.g. `docs/update-readme`)

```bash
git checkout main
git pull
git checkout -b feature/tema-2-exercises
```

## Commits

Write short messages in the imperative, starting with a type:

```
<type>: <what you did>
```

| Type | Use for |
|------|---------|
| `feat` | A new exercise or feature |
| `fix` | A bug fix |
| `docs` | Documentation or comments |
| `style` | Formatting only |

Examples: `feat: add exercise 3 with image gallery`, `docs: add JSDoc to tema_1`.

## Code

- Document every JavaScript function with [JSDoc](https://jsdoc.app/) (description, `@param` and `@returns`).
- Test your page in the browser and check the console for errors before committing.

## Pull requests

1. Push your branch and open a Pull Request to `main`.
2. Write a clear title and explain **what** you changed and **why**.
3. Another person reviews it before merging.
4. If a PR is rejected, the reviewer must write a comment explaining why.
5. After merging, delete the branch.
