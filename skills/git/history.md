# History Traps

## Reset

- `git reset --hard` pierde cambios uncommitted PERMANENTEMENTE — no hay undo
- `--hard` vs `--soft` vs `--mixed` — cada uno mueve diferentes cosas
- Reset de commit pushed = historia diverge — necesitas force push
- Reset con archivos untracked = untracked sobreviven — puede sorprender

## Revert

- Revert crea commit NUEVO — no borra el original
- Revert de merge commit necesita `-m 1` o `-m 2` — sin él, error
- Revert de revert = re-aplica cambios — historia confusa
- Revert de commit antiguo puede tener conflictos con commits posteriores

## Amend

- `--amend` cambia SHA — commit enmendado es commit DIFERENTE
- Amend de commit pushed = mismos problemas que rebase
- `--amend` sin staging = solo cambia mensaje
- Amend accidental en commit equivocado = reflog para recuperar

## Reflog

- Reflog es LOCAL — no se sincroniza con remote
- Reflog expira (default 90 días) — commits viejos perdidos
- `git gc` puede limpiar commits unreachable antes de expiración
- Reflog de branch borrada está en HEAD reflog, no branch reflog

## Interactive Rebase

- `pick` vs `reword` vs `edit` vs `squash` vs `fixup` — cada uno diferente
- Borrar línea en editor = commit ELIMINADO sin confirmación
- Reordenar commits que dependen entre sí = conflictos
- `drop` explícito más claro que borrar línea

## Cherry-Pick

- Cherry-pick NO relaciona los commits — son copias independientes
- Cherry-pick mismo commit dos veces = duplicado
- Cherry-pick de merge commit complicado — necesita `-m`
- Conflictos en cherry-pick = resolver manualmente cada uno
