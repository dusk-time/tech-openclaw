# Branching Traps

## Branch Creation

- `git checkout -b feature` desde branch equivocada = base incorrecta
- `git branch feature` sin checkout = sigues en branch anterior — commits van ahí
- Branch name con espacios falla silenciosamente en algunos tools
- `/` en branch name (feature/x) = algunos sistemas lo ven como directorio

## Switching

- `git checkout branch` con cambios uncommitted = pueden ir al nuevo branch — confuso
- `git switch` más seguro pero `-f` pierde cambios sin warning
- Stash automático no existe — cambios tracked bloqueantes, untracked se mezclan
- Checkout de branch con submodule diferente = submodule queda en estado anterior

## Merge

- Fast-forward merge no crea merge commit — historia lineal pero sin contexto
- `--no-ff` siempre crea merge commit — útil para features, ruido para fixes
- Merge de branch largo = mega merge commit difícil de revisar/revertir
- Branch borrada después de merge = commits huérfanos si no hay tag

## Rebase

- Rebase de branch publicada = historia diferente = otros deben `--force` pull
- Rebase interactivo mal hecho puede perder commits — reflog para recuperar
- Conflictos en rebase: resolver CADA commit, no solo una vez
- Rebase cambia SHAs — CI/CD references a commits viejos rotas

## Remote Tracking

- `git push -u origin feature` necesario la primera vez — sin `-u` no trackea
- Remote branch borrada no borra tracking local — `git fetch --prune` para limpiar
- `git pull` sin upstream configurado = error — `git branch --set-upstream-to`
- Remote rename no actualiza tracking branches — reconfigurar manualmente

## Naming Conventions

- Misma rama en dos remotes (origin/main, upstream/main) = confusión
- Branch name case-insensitive en Mac/Windows, sensitive en Linux — bugs CI
- Branch nombrada igual que tag = ambigüedad en algunos comandos
