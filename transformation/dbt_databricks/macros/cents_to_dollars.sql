{# Example reusable macro. Call as {{ cents_to_dollars('amount_cents') }} in a model. #}
{% macro cents_to_dollars(column_name, scale=2) %}
    round(cast({{ column_name }} as decimal(18, {{ scale }})) / 100, {{ scale }})
{% endmacro %}
