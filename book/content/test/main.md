# Test

This section exists for the sole purpose of experimenting with the Myst document engine. It will be omitted from the final product.

(my-section)=
## A section

Some content.

## Another section

[A link to the previous section.](#my-section)

## A test

(my-section)=
### Header _Targets_

Use `(label)=` before the element that you want to target, then reference content with:

* [](#my-section)

## Another test

```{math}
:label: my-math-label
e=mc^2
```

See [](#my-math-label) for an equation!