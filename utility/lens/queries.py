from typing import List


def get_profiles_query(wallet_addresses: List[str]) -> str:
    # we just limit it to 1, to get just one entry
    return f"""query Profiles {{
    profiles(request: {{ ownedBy: {wallet_addresses}, limit: 1 }}) {{
        items {{
        id
        name
        bio
        metadata
        handle
        stats {{
            totalFollowers
            totalFollowing
            totalPosts
            totalComments
            totalMirrors
            totalPublications
        }}
        ownedBy
        }}
        }}
    }}
    """.replace("'", '"')


def get_followers_query(user_id: str, offset: int = 0) -> str:
    return f"""query Followers {{
            followers(request: {{
                profileId: \"{user_id}\",
                limit: 50,
                cursor: "{{\\"offset\\":{offset}}}"
                }}) {{
                    items {{
                        wallet {{
                            address
                            defaultProfile {{
                                id
                                }}
                            }}
                        }}
                        pageInfo {{
                        prev
                        next
                        totalCount
                        }}
                    }}
        }}"""
