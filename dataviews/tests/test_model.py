from django.test import TestCase

from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF
from observationtypes.tests.model_factories import (
    ObservationTypeFactory, TextFieldFactory, NumericFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    DateTimeFieldFactory
)
from contributions.tests.model_factories import ObservationFactory

from ..models import View, Rule

from .model_factories import (
    ViewFactory, RuleFactory
)


class ViewTest(TestCase):
    def setUp(self):
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.view1_user = UserF.create()
        self.view2_user = UserF.create()
        self.non_member = UserF.create()
        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.view1 = ViewFactory(add_viewers=[self.view1_user], **{
            'project': self.project
        })
        self.view2 = ViewFactory(add_viewers=[self.view2_user], **{
            'project': self.project
        })

    @raises(View.DoesNotExist)
    def test_delete(self):
        self.view1.delete()
        View.objects.get(pk=self.view1.id)

    @raises(Rule.DoesNotExist)
    def test_delete_rules(self):
        rule = RuleFactory()
        rule.delete()
        self.assertEqual(rule.status, 'deleted')
        Rule.objects.get(pk=rule.id)

    def test_get_rules(self):
        RuleFactory(**{
            'status': 'active'
        })
        RuleFactory(**{
            'status': 'active'
        })
        inactive = RuleFactory(**{
            'status': 'deleted'
        })
        rules = Rule.objects.all()

        self.assertEqual(len(rules), 2)
        self.assertNotIn(inactive, rules)

    def test_get_data(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )

        RuleFactory(**{'view': view, 'observation_type': observation_type_1})

        self.assertEqual(len(view.data), 5)
        for observation in view.data:
            self.assertEqual(observation.observationtype, observation_type_1)

    def test_get_updated_data(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observation_type_1
        })

        observation = ObservationFactory(**{
            'project': project,
            'observationtype': observation_type_1,
            'attributes': {'text': 'yes to update'}
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'yes ' + str(x)}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'no ' + str(x)}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'text': 'yes'}
        })

        updater = UserF()
        update = {'text': 'yes, this has been updated', 'version': 1}
        observation.update(attributes=update, updator=updater)
        self.assertEqual(len(view.data), 6)

    def test_get_data_combined(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        observation_type_3 = ObservationTypeFactory(**{'project': project})
        view = ViewFactory(**{'project': project})
        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1}
            )
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2}
            )
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_3}
            )

        RuleFactory(**{'view': view, 'observation_type': observation_type_1})
        RuleFactory(**{'view': view, 'observation_type': observation_type_2})

        self.assertEqual(len(view.data), 10)
        for observation in view.data:
            self.assertNotEqual(
                observation.observationtype, observation_type_3)

    def test_get_data_text_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'text',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        TextFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'yes ' + str(x)}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'text': 'no ' + str(x)}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'bla': 'yes ' + str(x)}}
            )

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'text': 'yes'}
        })
        self.assertEqual(len(view.data), 5)

    def test_get_data_min_number_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 12}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 20}}
            )

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'number': 12}}
            )

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'number': {'minval': 15}}
        })

        self.assertEqual(len(view.data), 5)

    def test_get_data_max_number_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 12}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': 20}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'number': 12}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'number': {'maxval': 15}}
        })

        self.assertEqual(len(view.data), 5)

    def test_get_data_min_max_number_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'number',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        NumericFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': x}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'number': x}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'number': x}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'number': {'minval': 1, 'maxval': 4}}
        })

        self.assertEqual(len(view.data), 4)

    def test_get_data_true_false_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        TrueFalseFieldFactory(**{
            'key': 'true',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        TrueFalseFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'true': True, 'bla': 'bla'}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'true': False}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'true': True}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'true': True}
        })

        self.assertEqual(len(view.data), 5)

    def test_get_data_lookup_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        lookup_field = LookupFieldFactory(**{
            'key': 'lookup',
            'observationtype': observation_type_1
        })
        lookup_1 = LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        lookup_2 = LookupValueFactory(**{
            'name': 'Kermit',
            'field': lookup_field
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        lookup_field_2 = LookupFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })
        lookup_3 = LookupValueFactory(**{
            'name': 'Gonzo',
            'field': lookup_field_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'lookup': lookup_1.id}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'lookup': lookup_2.id}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'bla': lookup_3.id}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'lookup': [lookup_1.id, lookup_2.id]}
        })

        self.assertEqual(len(view.data), 10)

    def test_get_data_min_max_date_filter(self):
        project = ProjectF()
        observation_type_1 = ObservationTypeFactory(**{'project': project})
        DateTimeFieldFactory(**{
            'key': 'date',
            'observationtype': observation_type_1
        })
        observation_type_2 = ObservationTypeFactory(**{'project': project})
        DateTimeFieldFactory(**{
            'key': 'bla',
            'observationtype': observation_type_2
        })

        for x in range(0, 5):
            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'date': '2014-04-09'}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_1,
                'attributes': {'date': '2013-04-09'}
            })

            ObservationFactory(**{
                'project': project,
                'observationtype': observation_type_2,
                'attributes': {'bla': '2014-04-09'}
            })

        view = ViewFactory(**{'project': project})
        RuleFactory(**{
            'view': view,
            'observation_type': observation_type_1,
            'filters': {'date': {
                'minval': '2014-01-01', 'maxval': '2014-06-09 00:00'}
            }
        })

        self.assertEqual(len(view.data), 5)
