<!-- Extracted from SKILL.md for progressive disclosure; preserve section semantics. -->

### List with Images
```json
{
  "type": "Container",
  "$data": "${items}",
  "items": [
    {
      "type": "ColumnSet",
      "columns": [
        {
          "type": "Column",
          "width": "auto",
          "items": [
            {
              "type": "Image",
              "url": "${thumbnailUrl}",
              "size": "small",
              "$when": "${thumbnailUrl != null}"
            }
          ]
        },
        {
          "type": "Column",
          "width": "stretch",
          "items": [
            {
              "type": "TextBlock",
              "text": "${title}",
              "weight": "bolder",
              "wrap": true
            }
          ]
        }
      ]
    }
  ]
}
```

### Status Indicators
```json
{
  "type": "TextBlock",
  "text": "${status}",
  "color": "${if(status == 'Completed', 'good', if(status == 'In Progress', 'attention', 'default'))}"
}
```

### Currency Formatting
```json
{
  "type": "TextBlock",
  "text": "$${formatNumber(amount, 2)}"
}
```
