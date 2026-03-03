# Conflict Traps

## Detection

- Conflicto en archivo binario = git no puede mostrar diff — elegir versión completa
- Conflicto "both modified" vs "both added" — diferente resolución esperada
- Archivo renombrado + modificado = git puede no detectar rename — conflicto falso
- Whitespace-only conflicts escondidos si diff ignora whitespace

## Resolution

- Markers `<<<<<<<` olvidados en código = compila pero código roto
- Resolver "accept theirs" pero necesitabas "accept ours" = deshacer difícil
- Merge commit con conflicto mal resuelto = bug introducido silenciosamente
- `git checkout --ours` durante rebase = semántica invertida vs merge

## During Rebase

- Cada commit puede tener conflictos diferentes — resolver N veces, no 1
- Skip commit durante rebase = commit perdido sin warning claro
- `--continue` sin resolver todo = error, no merge parcial
- Abort rebase después de varios commits = vuelves al inicio, trabajo perdido

## Tool Issues

- Merge tool externo puede no guardar = git cree que resolviste pero archivo unchanged
- Merge tool que borra markers pero no combina código = silently wrong
- `git mergetool` genera `.orig` backups que pueden committearse por error
- Three-way merge tools: "local/remote/base" confuso durante rebase (invertido)

## Post-Resolution

- `git add` archivo conflictivo sin resolver todos los markers = commit roto
- Test suite no corre automáticamente después de merge — bugs post-merge
- Push sin pull de cambios del otro = force push necesario o más conflictos
- Merge commit sin mensaje descriptivo = arqueología difícil después

## Prevention

- Pull frecuente reduce pero no elimina conflictos
- Archivos grandes modificados por muchos = conflicto garantizado
- Refactors masivos sin coordinar = merge hell
- Branches muy largas = conflictos acumulados
