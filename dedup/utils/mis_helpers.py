import requests
from rest_framework.response import Response
from rest_framework import status
from auth_system.utils.session_key_utils import get_mis_auth_headers


def call_mis_api(request, url, params=None, timeout=30):
   
    headers, error_response = get_mis_auth_headers(request)
    if error_response:
        return error_response

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)

        if response.status_code != 200:
            try:
                error_data = response.json()
            except Exception:
                error_data = response.text or "Unknown error"

            return Response(
                {
                    "success": False,
                    "message": "MIS API request failed.",
                    "status_code": response.status_code,
                    "error": error_data,
                },
                status=response.status_code,
            )

        return Response(
            {
                "success": True,
                "message": "Data retrieved successfully.",
                "data": response.json(),
            },
            status=status.HTTP_200_OK,
        )

    except requests.RequestException as e:
        return Response(
            {
                "success": False,
                "message": "Unable to reach MIS service.",
                # "details": str(e),
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )
