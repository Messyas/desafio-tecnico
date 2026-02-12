from __future__ import annotations

from flask import jsonify, render_template_string

from . import api_bp
from ..services.openapi_spec import build_openapi_spec

SWAGGER_UI_TEMPLATE = r"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Tech Home API Docs</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css"
    />
    <style>
      html, body {
        margin: 0;
        background: #fafafa;
      }
      #swagger-ui {
        max-width: 1200px;
        margin: 0 auto;
      }
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
    <script>
      function resolveSpecUrl() {
        const pathname = window.location.pathname.replace(/\/+$/, '');
        if (pathname.endsWith('/docs')) {
          const prefix = pathname.slice(0, -5);
          return (prefix || '') + '/openapi.json';
        }
        return '/openapi.json';
      }

      window.ui = SwaggerUIBundle({
        url: resolveSpecUrl(),
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis
        ],
        layout: 'BaseLayout',
      });
    </script>
  </body>
</html>
"""


@api_bp.route("/openapi.json", methods=["GET"])
def openapi_json():
    return jsonify(build_openapi_spec())


@api_bp.route("/docs", methods=["GET"])
def swagger_ui():
    return render_template_string(SWAGGER_UI_TEMPLATE)
