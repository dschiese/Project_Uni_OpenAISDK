### Notizen

- Ein Agent kann viele Tools verwenden
- Keine Teams? Keine Interaktion zwischen Agenten? --> Gibt zumindest keine klassischen Team (vgl. AutoGen)
    -> Großer Anwendungseinsatz schwierig?
        -> Durch Tools wie Mem0 oder sonstiges ausgleichbar?
    -> Einsatz für kleine, smarte Anwendungsfälle
- Umgang mit lokalen Pfaden; durchsucher aller Dateien --> Nutzung von lokalem llama nicht möglich
- Schweres Tracking wenn Agenten als Tool auftreten
- Daten an andere Agenten weitergeben durch Tool schwierig
- Was geht in die AgentAsTools rein?
- Tool-Call AUfschlüsselung
- Error-Meldungen innerhalb der Tools => Debugging extrem schwierig
- Unintuitiv, dass andere Agenten als Tools verwendet werden
- Endbedingung definieren -> Macht LLms selbst
- Testing tool Nachvollziehbarkeit nicht gegeben
- Traces sehr gut!
- Falsche Arguemente aufgerufen
- Read file unendlich oft aufgerufen; loops?
    -> Agenten einbauen der an den Planner die relevanten Files gibt, ggf. Model mit sehr großem Kontext
- Read more files to fix bugs better -> More context -> Models that accept more
- Probiert, FAIL_TO_PASS tests zu inkludieren



---

- Let the planner identify the issue, or, the coder and invent a new agent "implementator"
- Only work on one file at a time?

---------

- Write results to file (Test and process)
- Use index as dir name
- Tool Ausgaben erscheinen immer vor Agenten Calls