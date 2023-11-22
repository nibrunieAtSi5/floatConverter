# floatConverter
Utility to convert between hardfloat and IEEE format


## Usage

```
python3 floatConverter/script_hardfloat_ieee.py --input-format <format> <command> <input value>
```



List of supported `command`:

* `recfntoieee` convert between hardfloat's recoded-format <format> to the IEEE encoding in the corresponding IEEE format`
*** `<format>` can be any of recf16, recf32, recf64.
* `ieeetorecfn` convert between IEEE format <format> to the corresponding hardfloat's recoded-format
*** `<format>` can be any of f16, f32, f64.

`<input value>` is an hexadecimal string, `_` separators are accepted.


## Example

```
python3 script_hardfloat_ieee.py ieeetorecfn --input-format f16 --unsafe-convert-to recf64 1f80
```
