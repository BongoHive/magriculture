# FIXME: This is the old cow lactation survey in the vumi.demos.decisiontree
#        poll format. It needs to be updated and hooked up to something.
#        See https://praekelt.onjira.com//browse/MAGRI-18.


TEST_YAML = '''
    __data__:
        url: 173.45.90.19/dis-uat/api/getFarmerDetails
        username: admin
        password: Admin1234
        params:
            - telNo
        json: >

    __start__:
        display:
            english: "Hello."
        next: farmers

    farmers:
        question:
            english: "Hi. There are multiple farmers with this phone number. Who are you?"
        options: name
        next: cows

    cows:
        question:
            english: "For which cow would you like to submit a milk collection?"
        options: name
        next: quantityMilked

    quantityMilked:
        question:
            english: "How much milk was collected?"
        validate: integer
        next: quantitySold

    quantitySold:
        question:
            english: "How much milk did you sell?"
        validate: integer
        next: milkTimestamp

    milkTimestamp:
        question:
            english: "When was this collection done?"
        options:
              - display:
                    english: "Today"
                default: today
                next: __finish__
              - display:
                    english: "Yesterday"
                default: yesterday
                next: __finish__
              - display:
                    english: "An earlier day"
                next:
                    question:
                        english: "Which day was it [dd/mm/yyyy]?"
                    validate: date
                    next: __finish__

    __finish__:
        display:
            english: "Thank you! Your milk collection was registered successfully."

    __post__:
        url: 173.45.90.19/dis-uat/api/addMilkCollections
        username: admin
        password: Admin1234
        params:
            - result
    '''
