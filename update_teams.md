# How-to Generate teams.json

Here are steps that were taken to create `teams.json` and how to update that data in the future, assuming the data still exists in the same format as before.

1. Visit [nhl.com](https://nhl.com)
2. Right click and select "View Page Source"
3. Search for "team_info"
4. Copy the block where `window.team_info` is declared
5. Paste into JSON formatter [like this website](https://jsonformatter.curiousconcept.com)
6. Remove any copied text around `[` and `]`
7. Format
8. Copy to clipboard
9. Paste into `teams.json`
