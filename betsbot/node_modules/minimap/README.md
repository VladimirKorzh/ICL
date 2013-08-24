# minimap

Simple, elegant data mapping and string templating without the bells and whistles.

## Require it

`var minimap = require('minimap');`

## Use it

`str = minimap.map({"token" : "value", "anothertoken" : "value2"}, "{token} {anothertoken}");`
`// str now contains "value value2"`

### Always replace

`minimap.always({"token" : "value"});`

### Never replace

`minimap.never({"token" : "value"});`