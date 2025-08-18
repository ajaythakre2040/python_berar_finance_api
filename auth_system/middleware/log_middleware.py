import uuid
import json
import jwt
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve, Resolver404
from auth_system.models import TblUser
from auth_system.models.login_session import LoginSession


class APILogMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        request._token = token

        # Identify session UUID
        session_uuid = None
        if token:
            try:
                session = LoginSession.objects.filter(
                    token=token, is_active=True
                ).first()
                if session:
                    session_uuid = str(session.session_id or session.pk)
            except Exception as e:
                print(f"[Middleware] Error fetching session: {e}")

        # Set request UUID
        if session_uuid:
            request.uniqid = session_uuid
        else:
            request.uniqid = str(uuid.uuid4())

        request.session["session_uuid"] = request.uniqid
        request.session.modified = True

        # Parse body data
        try:
            if request.body:
                request._body_data = json.loads(request.body.decode("utf-8"))
            else:
                request._body_data = {}
        except Exception:
            request._body_data = {}

        request._query_params = _flatten_querydict(
            request.GET,
            exclude_keys=["page", "page_size", "limit", "offset"],
        )

    def process_response(self, request, response):
        try:
            # Check for double logging based on a unique request ID
            if getattr(request, "_log_saved", False):
                return response

            # Check if the URL resolves to a known view
            try:
                resolve(request.path_info)
            except Resolver404:
                # If the URL doesn't resolve, it's likely a duplicate or an invalid request
                return response

            path = request.path_info
            method = request.method

            # Skip logging for static, admin, health-check endpoints
            if (
                path.startswith("/static/")
                or path.startswith("/admin/")
                or path == "/health/"
            ):
                return response

            user = getattr(request, "user", None)
            user_obj = user if user and user.is_authenticated else None

            token = request._token
            body_data = getattr(request, "_body_data", {})
            query_params = getattr(request, "_query_params", {})

            app_name = None
            if path == "/auth_system/login/" or path == "/auth_system/logout/":
                app_name = "dedup"
            elif path.startswith("/dedup/"):
                app_name = "dedup"
            elif path.startswith("/auth_system/"):
                app_name = "auth_system"

            if not app_name:
                return response  # Only log for selected apps

            # Extra logic to determine user (especially during login/logout)
            if not user_obj:
                if path == "/auth_system/login/":
                    username = body_data.get("username")
                    if username:
                        try:
                            if username.isdigit() and len(username) == 10:
                                user_obj = TblUser.objects.filter(
                                    mobile_number=username
                                ).first()
                            elif "@" in username:
                                user_obj = TblUser.objects.filter(
                                    email=username
                                ).first()
                            else:
                                user_obj = TblUser.objects.filter(
                                    username=username
                                ).first()
                        except Exception:
                            user_obj = None

                elif path == "/auth_system/logout/" and token:
                    try:
                        session = LoginSession.objects.filter(
                            token=token, is_active=True
                        ).first()
                        if session and hasattr(session, "user"):
                            user_obj = session.user
                    except Exception as e:
                        print(f"[Middleware] Error fetching logout session user: {e}")

            # On successful login, extract and save the new session UUID from response
            if path == "/auth_system/login/":
                if (
                    response.status_code == 200
                    and hasattr(response, "content")
                    and response.get("Content-Type", "").startswith("application/json")
                ):
                    try:
                        data = json.loads(response.content.decode("utf-8"))
                        new_uuid = data.get("session_uuid")
                        if new_uuid:
                            request.uniqid = new_uuid
                            request.session["session_uuid"] = new_uuid
                            request.session.modified = True
                    except Exception as e:
                        print(f"[Middleware] Failed to parse login response UUID: {e}")

            # Prepare request data for logging
            if method == "GET" and not query_params:
                request_data = {"message": "Full data fetched"}
            else:
                request_data = {**body_data, **query_params}

            # Import the appropriate APILog model
            APILog = self._import_apilog_model(app_name)
            if not APILog:
                return response

            # Create the log entry
            log_entry = APILog(
                uniqid=request.uniqid,
                user=user_obj,
                method=method,
                endpoint=path,
                request_data=request_data,
                response_status=response.status_code,
            )

            # Add response data if it's JSON
            try:
                if hasattr(response, "content") and response.get(
                    "Content-Type", ""
                ).startswith("application/json"):
                    log_entry.response_data = json.loads(
                        response.content.decode("utf-8")
                    )
                else:
                    log_entry.response_data = None
            except Exception:
                log_entry.response_data = None

            log_entry.save()
            request._log_saved = True  # ✅ Prevent duplicate logging

        except Exception as e:
            print(f"[Middleware] APILog error: {e}")

        return response

    def _import_apilog_model(self, app_name):
        try:
            module = __import__(f"{app_name}.models", fromlist=["APILog"])
            return getattr(module, "APILog")
        except (ImportError, AttributeError) as e:
            print(f"[Middleware] Could not import APILog from {app_name}.models: {e}")
            return None


def _flatten_querydict(querydict, exclude_keys=None):
    exclude_keys = exclude_keys or []
    return {
        key: (value[0] if len(value) == 1 else value)
        for key, value in querydict.lists()
        if key not in exclude_keys
    }
