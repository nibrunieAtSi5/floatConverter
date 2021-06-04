# floatConverter
Utility to convert between hardfloat and IEEE format


## Usage

```
python3 floatConverter/script_hardfloat_ieee.py --input-size <bitsize> <command> <input value>
```

`<bitsize>` can be any of 16, 32, 64.


List of supported `command`:
* `recfntoieee` convert between hardfloat's recoded-format of size `bitsize` to IEEE encoding of size `bitsize`

`<input value>` is an hexadecimal string, `_` separators are accepted.


## Example

```
python3 floatConverter/script_hardfloat_ieee.py --input-size 64 recfntoieee 0_8287_c7b7_ccdd_d1fa
```
