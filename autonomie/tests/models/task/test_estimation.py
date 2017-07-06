# -*- coding: utf-8 -*-
# * Authors:
#       * TJEBBES Gaston <g.t@majerti.fr>
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
import datetime
import colander
import pytest
from colanderalchemy import SQLAlchemySchemaNode


def test_payment_line_description():
    from autonomie.models.task.estimation import PaymentLine
    schema = SQLAlchemySchemaNode(PaymentLine, includes=('description',))
    schema = schema.bind()
    value = {'description': "test\n"}
    assert schema.deserialize(value) == value
    value = {'description': "\n"}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)


def test_payment_line_amount():
    from autonomie.models.task.estimation import PaymentLine
    schema = SQLAlchemySchemaNode(PaymentLine, includes=('amount',))
    schema = schema.bind()

    value = {'amount': 12.5}
    assert schema.deserialize(value) == {'amount': 1250000}

    value = {'amount': 'a'}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)
    value = {}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)


def test_payment_line_date():
    import datetime
    from autonomie.models.task.estimation import PaymentLine
    schema = SQLAlchemySchemaNode(PaymentLine, includes=('date',))
    schema = schema.bind()
    value = {'date': datetime.date.today().isoformat()}
    assert schema.deserialize(value) == {'date': datetime.date.today()}
    value = {}
    assert schema.deserialize(value) == value


def test_payment_line_task_id():
    from autonomie.models.task.estimation import PaymentLine
    schema = SQLAlchemySchemaNode(PaymentLine, includes=('task_id',))
    value = {'task_id': 5}
    assert schema.deserialize(value) == value
    value = {}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)


def test_payment_line():
    from autonomie.models.task.estimation import PaymentLine
    schema = SQLAlchemySchemaNode(PaymentLine)
    schema = schema.bind()

    value = {
        'task_id': 5,
        'date': datetime.date.today().isoformat(),
        'amount': 12.5,
        'description': u"Description"
    }
    expected_value = {
        'task_id': 5,
        'date': datetime.date.today(),
        'amount': 1250000,
        'description': u"Description",
        'order': 1
    }
    assert schema.deserialize(value) == expected_value


def test_estimation_signed_status():
    from autonomie.models.task.estimation import Estimation
    schema = SQLAlchemySchemaNode(Estimation, includes=('signed_status',))
    schema = schema.bind()

    value = {'signed_status': u"signed"}
    assert schema.deserialize(value) == value

    value = {'signed_status': u"error"}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)


def test_estimation_deposit():
    from autonomie.models.task.estimation import Estimation

    schema = SQLAlchemySchemaNode(Estimation, includes=('deposit',))
    schema = schema.bind()

    value = {'deposit': 15}
    assert schema.deserialize(value) == value

    value = {'deposit': 150}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)

    value = {'deposit': -1}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)


def test_estimation_paymentDisplay():
    from autonomie.models.task.estimation import Estimation

    schema = SQLAlchemySchemaNode(Estimation, includes=('paymentDisplay',))
    schema = schema.bind()

    value = {'paymentDisplay': u'SUMMARY'}
    assert schema.deserialize(value) == value

    value = {}
    assert schema.deserialize(value) == {'paymentDisplay': u'NONE'}

    value = {'paymentDisplay': u'ERROR'}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)


def test_estimation_payment_lines():
    from autonomie.models.task.estimation import Estimation
    schema = SQLAlchemySchemaNode(Estimation, includes=('payment_lines',))
    schema = schema.bind()

    value = {'payment_lines': []}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)

    value = {}
    with pytest.raises(colander.Invalid):
        schema.deserialize(value)

    value = {'payment_lines': [
        {
            'task_id': 5,
            'date': datetime.date.today().isoformat(),
            'amount': 12.5,
            'description': u"Description"
        }
    ]}
    expected_value = {
        'payment_lines': [
            {
                'task_id': 5,
                'date': datetime.date.today(),
                'amount': 1250000,
                'description': u"Description",
                'order': 1
            }
        ]
    }
    assert schema.deserialize(value) == expected_value


def test_estimation(unity, tva):
    from autonomie.models.task.estimation import Estimation
    schema = SQLAlchemySchemaNode(Estimation)
    schema = schema.bind()

    value = {
        "name": u"Devis 1",
        'date': datetime.date.today().isoformat(),
        'address': u"adress",
        "description": u"description",
        "paymentDisplay": u"SUMMARY",
        "deposit": 5,
        "signed_status": "signed",
        'line_groups': [
            {
                'task_id': 5,
                'title': u"title",
                'description': u"description",
                "order": 5,
                'lines': [
                    {
                        'cost': 15,
                        'tva': 20,
                        'description': u'description',
                        'unity': u"Mètre",
                        "quantity": 5,
                        "order": 2,
                    }
                ]
            }
        ],
        'payment_lines': [
            {
                'task_id': 5,
                'date': datetime.date.today().isoformat(),
                'amount': 12.5,
                'description': u"Description",
                "order": 8
            }
        ],
    }
    expected_value = {
        "name": u"Devis 1",
        'date': datetime.date.today(),
        'address': u"adress",
        "description": u"description",
        "paymentDisplay": u"SUMMARY",
        "deposit": 5,
        "signed_status": "signed",
        'line_groups': [
            {
                'task_id': 5,
                'title': u"title",
                'description': u"description",
                "order": 5,
                'lines': [
                    {
                        'cost': 1500000,
                        'tva': 2000,
                        'description': u'description',
                        'unity': u"Mètre",
                        "quantity": 5.0,
                        "order": 2,
                    }
                ]
            }
        ],
        'payment_lines': [
            {
                'task_id': 5,
                'date': datetime.date.today(),
                'amount': 1250000,
                'description': u"Description",
                "order": 8
            }
        ],
    }
    # Check those values are valid
    result = schema.deserialize(value)
    for key, value in expected_value.items():
        assert result[key] == value