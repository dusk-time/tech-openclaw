# Collaboration Traps

## Push/Pull

- `git pull` = fetch + merge — puede crear merge commits inesperados
- `git pull --rebase` evita merge commits pero puede tener conflictos
- Push rechazado por non-fast-forward ≠ necesitas force — primero pull
- `--force` sobreescribe historia de otros — `--force-with-lease` más seguro

## Force Push

- `--force` ignora cambios de otros — commits de compañeros perdidos
- `--force-with-lease` falla si remote cambió — más seguro pero no infalible
- Force push a main/master = CI/CD references rotas, deploys fallidos
- Protección de branch en GitHub/GitLab evita force push — configurar siempre

## Remote Branches

- `git fetch` no actualiza working directory — solo refs
- Branch tracking no se actualiza automáticamente si remote renombra
- `origin` es convención, no requirement — pueden existir otros remotes
- `git remote prune origin` limpia refs pero no branches locales

## Code Review

- Push durante review = commits nuevos no necesariamente revisados
- Force push durante review = diff cambia, comments pueden quedar obsoletos
- Approve antes de CI completo = bugs merged
- Squash merge pierde historia de commits individuales

## Hooks

- Hooks locales no se comparten — cada dev debe configurar
- Hook lento = push/commit lento — developers lo bypasean con `--no-verify`
- Server-side hooks vs client-side hooks — server es enforceable
- Hook que falla en un OS pero no otro — CI sorpresas

## Submodules

- Clone sin `--recurse-submodules` = submodules vacíos
- Submodule actualizado pero commit padre no = versión vieja checked out
- Cambios en submodule sin commit en padre = cambios perdidos para otros
- Submodule URL cambiada = otros devs deben `git submodule sync`
