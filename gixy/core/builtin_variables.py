from gixy.core.regexp import Regexp
from gixy.core.variable import Variable


BUILTIN_VARIABLES = {
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_uri
    'uri': '/[^\x20\t]*',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_document_uri
    'document_uri': '/[^\x20\t]*',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_arg_
    'arg_': '[^\s&]+',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_args
    'args': '[^\s]+',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_query_string
    'query_string': '[^\s]+',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_uri
    'request_uri': '/[^\s]*',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_http_
    'http_': '[\x21-\x7e]',

    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_http_
    'upstream_http_': '',
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_cookie_
    'upstream_cookie_': '',
    # http://nginx.org/en/docs/http/ngx_http_proxy_module.html#var_proxy_add_x_forwarded_for
    'proxy_add_x_forwarded_for': '',
    # http://nginx.org/en/docs/http/ngx_http_proxy_module.html#var_proxy_host
    'proxy_host': '',
    # http://nginx.org/en/docs/http/ngx_http_proxy_module.html#var_proxy_port
    'proxy_port': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_proxy_protocol_addr
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_proxy_protocol_addr
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_proxy_protocol_port
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_proxy_protocol_port
    'proxy_protocol_port': '',
    # http://nginx.org/en/docs/http/ngx_http_fastcgi_module.html#var_fastcgi_path_info
    'fastcgi_path_info': '',
    # http://nginx.org/en/docs/http/ngx_http_fastcgi_module.html#var_fastcgi_script_name
    'fastcgi_script_name': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_content_type
    'content_type': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_cookie_
    'cookie_': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_host
    'host': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_hostname
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_hostname
    'hostname': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_limit_rate
    'limit_rate': '',
    # http://nginx.org/en/docs/http/ngx_http_memcached_module.html#var_memcached_key
    'memcached_key': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_realpath_root
    'realpath_root': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_remote_user
    'remote_user': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request
    'request': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_body
    'request_body': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_completion
    'request_completion': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_filename
    'request_filename': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_id
    'request_id': '',
    # http://nginx.org/en/docs/http/ngx_http_slice_module.html#var_slice_range
    'slice_range': '',
    # http://nginx.org/en/docs/http/ngx_http_secure_link_module.html#var_secure_link
    'secure_link': '',
    # http://nginx.org/en/docs/http/ngx_http_secure_link_module.html#var_secure_link_expires
    'secure_link_expires': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_sent_http_
    'sent_http_': '',
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_server_name
    'server_name': '',

    # "Secure" variables that can't content or strictly limited user input

    # http://nginx.org/en/docs/http/ngx_http_browser_module.html#var_ancient_browser
    'ancient_browser': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_binary_remote_addr
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_binary_remote_addr
    'binary_remote_addr': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_body_bytes_sent
    'body_bytes_sent': None,
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_bytes_received
    'bytes_received': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_bytes_sent
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_bytes_sent
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_bytes_sent
    'bytes_sent': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_connection
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_connection
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_connection
    'connection': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_connection_requests
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_connection_requests
    'connection_requests': None,
    # http://nginx.org/en/docs/http/ngx_http_stub_status_module.html#var_connections_active
    'connections_active': None,
    # http://nginx.org/en/docs/http/ngx_http_stub_status_module.html#var_connections_reading
    'connections_reading': None,
    # http://nginx.org/en/docs/http/ngx_http_stub_status_module.html#var_connections_waiting
    'connections_waiting': None,
    # http://nginx.org/en/docs/http/ngx_http_stub_status_module.html#var_connections_writing
    'connections_writing': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_content_length
    'content_length': None,
    # http://nginx.org/en/docs/http/ngx_http_ssi_module.html#var_date_gmt
    'date_gmt': None,
    # http://nginx.org/en/docs/http/ngx_http_ssi_module.html#var_date_local
    'date_local': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_document_root
    'document_root': '/etc/nginx',
    # http://nginx.org/en/docs/http/ngx_http_geoip_module.html
    # http://nginx.org/en/docs/stream/ngx_stream_geoip_module.html
    'geoip_': None,
    # http://nginx.org/en/docs/http/ngx_http_gzip_module.html#var_gzip_ratio
    'gzip_ratio': None,
    # http://nginx.org/en/docs/http/ngx_http_v2_module.html#var_http2
    'http2': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_https
    'https': None,
    # http://nginx.org/en/docs/http/ngx_http_referer_module.html#var_invalid_referer
    'invalid_referer': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_is_args
    'is_args': None,
    # http://nginx.org/en/docs/http/ngx_http_auth_jwt_module.html
    'jwt_': None,
    # http://nginx.org/en/docs/http/ngx_http_browser_module.html#var_modern_browser
    'modern_browser': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_msec
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_msec
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_msec
    'msec': None,
    # http://nginx.org/en/docs/http/ngx_http_browser_module.html#var_msie
    'msie': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_nginx_version
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_nginx_version
    'nginx_version': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_pid
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_pid
    'pid': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_pipe
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_pipe
    'pipe': None,
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_protocol
    'protocol': None,
    # http://nginx.org/en/docs/http/ngx_http_realip_module.html#var_realip_remote_addr
    # http://nginx.org/en/docs/stream/ngx_stream_realip_module.html#var_realip_remote_addr
    # http://nginx.org/en/docs/http/ngx_http_realip_module.html#var_realip_remote_port
    # http://nginx.org/en/docs/stream/ngx_stream_realip_module.html#var_realip_remote_port
    'realip_remote_port': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_remote_addr
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_remote_addr
    'remote_addr': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_remote_port
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_remote_port
    'remote_port': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_body_file
    'request_body_file': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_length
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_request_length
    'request_length': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_method
    'request_method': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_time
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_request_time
    'request_time': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_scheme
    'scheme': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_server_addr
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_server_addr
    'server_addr': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_server_port
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_server_port
    'server_port': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_server_protocol
    'server_protocol': None,
    # http://nginx.org/en/docs/http/ngx_http_session_log_module.html#var_session_log_binary_id
    'session_log_binary_id': None,
    # http://nginx.org/en/docs/http/ngx_http_session_log_module.html#var_session_log_id
    'session_log_id': None,
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_session_time
    'session_time': None,
    # http://nginx.org/en/docs/http/ngx_http_spdy_module.html#var_spdy
    'spdy': None,
    # http://nginx.org/en/docs/http/ngx_http_spdy_module.html#var_spdy_request_priority
    'spdy_request_priority': None,
    # http://nginx.org/en/docs/http/ngx_http_ssl_module.html
    # http://nginx.org/en/docs/stream/ngx_stream_ssl_module.html
    'ssl_': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html#var_status
    # http://nginx.org/en/docs/http/ngx_http_log_module.html#var_status
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html#var_status
    'status': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html
    'tcpinfo_': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html
    # http://nginx.org/en/docs/http/ngx_http_log_module.html
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html
    'time_iso8601': None,
    # http://nginx.org/en/docs/http/ngx_http_core_module.html
    # http://nginx.org/en/docs/http/ngx_http_log_module.html
    # http://nginx.org/en/docs/stream/ngx_stream_core_module.html
    'time_local': None,
    # http://nginx.org/en/docs/http/ngx_http_userid_module.html#var_uid_got
    'uid_got': None,
    # http://nginx.org/en/docs/http/ngx_http_userid_module.html#var_uid_reset
    'uid_reset': None,
    # http://nginx.org/en/docs/http/ngx_http_userid_module.html#var_uid_set
    'uid_set': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_addr
    # http://nginx.org/en/docs/stream/ngx_stream_upstream_module.html#var_upstream_addr
    'upstream_addr': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_bytes_received
    # http://nginx.org/en/docs/stream/ngx_stream_upstream_module.html#var_upstream_bytes_received
    'upstream_bytes_received': None,
    # http://nginx.org/en/docs/stream/ngx_stream_upstream_module.html#var_upstream_bytes_sent
    'upstream_bytes_sent': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_cache_status
    'upstream_cache_status': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_connect_time
    # http://nginx.org/en/docs/stream/ngx_stream_upstream_module.html#var_upstream_connect_time
    'upstream_connect_time': None,
    # http://nginx.org/en/docs/stream/ngx_stream_upstream_module.html#var_upstream_first_byte_time
    'upstream_first_byte_time': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_header_time
    'upstream_header_time': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_response_length
    'upstream_response_length': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_response_time
    'upstream_response_time': None,
    # http://nginx.org/en/docs/stream/ngx_stream_upstream_module.html#var_upstream_session_time
    'upstream_session_time': None,
    # http://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_status
    'upstream_status': None
}


def is_builtin(name):
    if isinstance(name, int):
        # Indexed variables can't be builtin
        return False
    for builtin in BUILTIN_VARIABLES:
        if builtin.endswith('_'):
            if name.startswith(builtin):
                return True
        elif name == builtin:
            return True
    return False


def builtin_var(name):
    for builtin, regexp in BUILTIN_VARIABLES.items():
        if builtin.endswith('_'):
            if not name.startswith(builtin):
                continue
        elif name != builtin:
            continue

        if regexp:
            return Variable(name=name, value=Regexp(regexp, strict=True, case_sensitive=False))
        return Variable(name=name, value='builtin', have_script=False)
    return None
