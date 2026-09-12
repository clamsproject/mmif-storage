# Developer Notes

[Index](notes.md)


## Parameters

Parameters are handed in to a CLAMS app in several ways (see the [CLAMS App user manual](https://clams.ai/clams-python/clamsapp.html)).

First is as a set of variables handed in via the HHTP query string (note that the manual above seems to have a mistake, it adds a slash before the question mark):

```bash
curl -X POST -d@input.mmif "http://app-server:5000?pretty=True"
```

These variables are entered as strings and converted into the right type by a parameter caster.

The second is via a JSON envelope, where the MMIF object is embedded with the parameters in a larger object. In this case the parameters have the types as they are expected by the application:

```json
{
  "parameters": {
    "prompt": "A very long prompt that would not fit in a query string...",
    "labelMap": {"B": "bars", "S": "slate"},
    "temperature": 0.7,
    "pretty": true
  },
  "mmif": {
    "metadata": { "mmif": "..." },
    "documents": [ "..." ],
    "views": []
  }
}
```

The third is some comination of the above