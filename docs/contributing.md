# Contributing

A primary goal of the library is to be extendable and flexbile to easily allow developers to build access to datasources, regardless of how those datasources are exposed.  For the moment, this document will give a high level overview of how to add a new datasource to the library.  As the interface is refined over the next few releases so will this document.

## Datasource Overview

A datasource is essentially a wrapper of the underlying API which translates between STAC-compliant and API-compliant requests/responses.  It inherits a standard pattern, defined simply in the [sources.base.Datasource](../datasources/sources/base.py) base class, but more realistically looks something like this:

```python
from .base import Datasource
from datasources.stac.query import STACQuery
from datasources.stac.item import STACItem

class MyDatasource(Datasource):
    
    stac_compliant = False
    tags = ['Raster', 'MS']
    
    def __init__(self, manifest):
        self.manifest = manifest
       
    def search(self, spatial, temporal=None, properties=None, limit=10, **kwargs):
        stac_query = STACQuery(spatial, temporal)
        
        
        request = # logic to parse user input into API request
        
        self.manifest.sources.append([self, request])
        
    def execute(self, query):
        response = # query API with request
        
        stac_item = # logic to parse response into STAC item
        
        STACItem.load(stac_item) # soft schema validation
        
        return [stac_item]
```
There a couple of things happening here, let's go over them.

##### Class Attributes
- **stac_compliant** indicates whether or not the underlying API is STAC compliant.  Used internally for orchestration.
- **tags** are used to sort datasources into functional groups for querying (see [datasources.sources.__init__.py](../datasources/sources/__init__.py)).

##### Init
- The only required input parameter is the manifest, which is essentially a context manager for performing multiple queries from multiple datasources in parallel.  

##### Search method
- The search method takes the STAC compliant user input and generates an API-compatible request.
- User input is seperated into a couple parameters:
  - **spatial**: geojson geometry representing the spatial extent of the query.
  - **temporal**: temporal range representing the temporal extent of the query.
  - **properties**: STAC or legacy properties used to query the API and/or filter the response.
  - **limit**: limits response to a maximum number of returned items.
  - **kwargs**: API-specific keyword arguments.
- The [datasources.stac.query.STACQuery](../datasources/stac/query.py) object validates the user input to ensure it is STAC compliant, and provides some handy methods such as bounding box calculation and temporal filtering.
- The API request and a reference to the datasource is appended to **self.manifest.sources**

##### Execute method
- The **query** parameter of the execute method receives the API request created in the search method.
- Ping the API and implement logic to parse the response into a valid STAC item.
- The [datasources.stac.item.STACITem](../datasources/stac/item.py) object performs a soft validation of the STAC Item to ensure all the required fields are present.
- If the API is STAC compliant, the execute method should return the API response without any modification.  If the API is not STAC compliant, it should return a list of STAC Items.

### Example
Datasources also must define an **example** method which is used to populate the [examples](examples/) found in the documentation and to perform more rigorous STAC schema validation.  Although the geometry used to perform the query will change (different datasources have different spatial extents), the pattern will generally look like this:

```python
def example(self):
    geoj = # valid geojson geometry
    self.search(geoj)
    response = self.manifest.execute()
    return response
```

Calling `self.search()` appends the search to the manifest.  Calling `manifest.execute()` calls the execute method of each datasource appended to the manifest and splits the load across multiple processes via the `datasources.base.Datasource.execute_multi` wrapper.

### Finishing Up
Once the datasource itself is finished, there are a few final steps:
1. Build and validate an example STAC Item with the [CLI script](../datasources/scripts/_cli.py).
2. Write [test cases](../../tests)
3. Update the documentation [here](datasource-reference.md), [here](README.md), and [here](../README.md)

You can now query your datasource as follows!

```python
from datasources import Manifest

manifest = Manifest()
manifest.load_source('MyDatasource')

manifest['MyDatasource'].search(geojson_geometry)

response = manifest.execute()
```

