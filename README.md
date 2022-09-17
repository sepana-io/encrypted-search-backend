# Encrypted Search Engine - backend

This repository serves as the backend for the Encrypted Search Engine project built during [EthBerlin 2022](https://ethberlin.ooo/).

This backend provides you with the following APIs:

<hr>

1. Indexing the encrypted data

Every encrypted data point added by the user via [encrypted.sepana.io](encrypted.sepana.io) calls the indexing endpoint for being indexed, so that it can be later made searchable.

Two endpoints which can be used for indexing are as follows:

a. Single document indexing

Endpoint
```
/v1/index
```

Curl request: 

```bash
curl --location --request POST 'https://<HOST>:<PORT>/v1/index' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "text": "<YOUR_ENCRYPTED_MESSAGE>",
        "shared": true,
        "creator_address": "<YOUR ENCRYPTED ADDRESS>",
        "shared_addresses": ["<LIST>", "<OF>", "<ENCRYPTED>", "<OF FRIENDS/FOLLOWERS>"],
        "document_type": "<text/ipfs>"
}'
```

Sample Response: 

```json
{
    "message": "document indexed successfully"
}
```

b. Bulk Indexing

Endpoint:

```
/v1/bulk_index
```

Input Data Schema:
```
List[
    DataIngestionSchema{
    text*	string
    title: Text
    shared*	boolean
    title: Shared
    creator_address*	string
    title: Creator Address
    shared_addresses*	Shared Addresses[...]
    document_type*	DocumentTypestring
    title: DocumentType
    An enumeration.
    Enum:
    Array [ 3 ]
    }
]
```
<hr>

2. Fetch user information

We need this to be able to allow the user to share their encrypted data with people in their circles.

We have used [Lens APIs](https://lens.xyz/) for fetching this information.
It comprises of two endpoints. The first one fetches the user's information from the Lens network using their wallet address. 

Once, the user information is available, that be used to fetch the users in their circles (with whom their messages can be shared). For our use cases, we have fetched the information about their followers.

Endpoints:

a. Fetch user information - it internally uses https://docs.lens.xyz/docs/get-profiles


```
curl --location --request POST 'https://<HOST>:<PORT>/v1/user/info' \
--header 'Content-Type: application/json' \
--data-raw '{
    "wallet_address": "<USER_WALLET_ADDRESS>"
}'
```
Example response:
```
{
    "id": "<USER_ID>",
    "name": "<NAME OF THE USER>",
    "bio": "<USER_BIO>",
    "metadata": "<USER_METADATA>",
    "handle": "<USER_HANDLE>",
    "stats": {
        "totalFollowers": 50,
        "totalFollowing": 3,
        "totalPosts": 7,
        "totalComments": 0,
        "totalMirrors": 0,
        "totalPublications": 7
    },
    "ownedBy": "<USER_WALLET_ADDRESS>"
}
```

b. Fetch user's followers - it internally uses https://docs.lens.xyz/docs/followers

```
curl --location --request POST 'https://<HOST>:<PORT>/v1/user/followers' \
--header 'Content-Type: application/json' \
--data-raw '{
    "user_lens_id": "<USER_ID>"
}'
```

Example response:
```
[
    {
        "wallet": {
            "address": "0xc9E5E1338BBceA936F0404870C6F86a2a9BAD767",
            "defaultProfile": {
                "id": "0x3181"
            }
        }
    },
    {
        "wallet": {
            "address": "0x4F1B38512DEfc7CE6083ce30Fec91cC967e538E4",
            "defaultProfile": null
        }
    },
    {
        "wallet": {
            "address": "0x5e27a0de706BADeCC3747278DF46dAd150defBA0",
            "defaultProfile": null
        }
    },
    {
        "wallet": {
            "address": "0x0Fc590a6a5D82BAEdc93885EA7aAd9F928b4dF58",
            "defaultProfile": null
        }
    },
    {
        "wallet": {
            "address": "0x933648509afA0a8C9D31068061a74fe2F7175cDf",
            "defaultProfile": null
        }
    },
    {
        "wallet": {
            "address": "0xA0f6D205218c76c0dF71cE417ED924b95eAdeE57",
            "defaultProfile": null
        }
    }
]
```

<hr>

3. Search - This serves as endpoint which returns the results back from the indexed data while the users search for them

```
SearchQuerySchema{
text	string
title: Text
default:
shared	string
title: Permission
default: all
An enumeration.

Enum:
Array [ 3 ]
creator_address	string
title: Creator Address
document_type	string
title: DocumentType
default: all
An enumeration.

Enum:
Array [ 3 ]
date_sort	string
title: DateSort
default: desc
An enumeration.

Enum:
Array [ 2 ]
from_date	string($date)
title: From Date
to_date	string($date)
title: To Date
page	integer
title: Page
default: 1
size	integer
title: Size
default: 10
 
}
```

Sample Query:
```
curl --location --request POST 'https://<HOST>:<PORT>/v1/search' \
--header 'Content-Type: application/json' \
--data-raw '{
    "text": "<ENCRYPTED-KEYWORD/S>",
    "shared": "all",
    "document_type": "text"
}'
```

Sample Response:
```
{
    "query": {
        "text": "<ENCRYPTED-KEYWORD/S>",
        "shared": "all",
        "creator_address": null,
        "document_type": "text",
        "date_sort": "desc",
        "from_date": null,
        "to_date": null,
        "page": 1,
        "size": 10
    },
    "total_count": 1,
    "data": [
        {
            "_index": "encrypted_index_ethberlin",
            "_id": "83ppS4MBGAmQiiA7Br5C",
            "_score": null,
            "_source": {
                "text": "<ENCRYPTE_MESSAGE>",
                "shared": true,
                "created_address": "",
                "shared_addresses": [],
                "document_type": "text",
                "created": "2022-09-17T14:25:17.540705"
            },
            "sort": [
                1663424717540
            ]
        }
    ]
}
```

<hr>
 Run the application:

1. Activate the Python virtual environment (Python 3.8+)

2. Install the dependencies
```
pip install -r requirements.txt
```

3. Run the application
```
python run.py
```

<hr>

If you any doubts, please contact daniel@sepana.io

<hr>