// Tests for magri-ussd.js

var assert = require("assert");
var vumigo = require("vumigo_v01");
var app = require("../lib/magri-ussd");
var test_utils = vumigo.test_utils;


// This just checks that you hooked you InteractionMachine
// up to the api correctly and called im.attach();
describe("test_api", function() {
    it("should exist", function() {
        assert.ok(app.api);
    });
    it("should have an on_inbound_message method", function() {
        assert.ok(app.api.on_inbound_message);
    });
    it("should have an on_inbound_event method", function() {
        assert.ok(app.api.on_inbound_event);
    });
});

var tester;

var test_fixtures_full = [
    "test/fixtures/farmer.json",
    "test/fixtures/highest_markets.json",
    "test/fixtures/markets.json",
    "test/fixtures/markets_1.json",
    "test/fixtures/price_history.json",
    "test/fixtures/price_history_market2.json",
    "test/fixtures/price_history_none.json",
    "test/fixtures/district.json",
    "test/fixtures/crop.json",
];

var test_fixtures_registration = [
    "test/fixtures/farmer_404.json",
    "test/fixtures/district.json",
    "test/fixtures/crop.json",
    "test/fixtures/farmer_post.json",
    "test/fixtures/user_post.json",
    "test/fixtures/actor.json",
];


describe("as an unregistered farmer", function() {

    var fixtures = test_fixtures_registration;
    beforeEach(function() {
        tester = new vumigo.test_utils.ImTester(app.api, {
            custom_setup: function (api) {
                api.config_store.config = JSON.stringify({
                    lima_links_api: {
                        url: "http://qa/api/v1/",
                        username: "test",
                        password: "password",
                    }
                });

                var dummy_contact = {
                    key: "f953710a2472447591bd59e906dc2c26",
                    surname: "Trotter",
                    user_account: "test-0-user",
                    bbm_pin: null,
                    msisdn: +1111111,
                    created_at: "2013-04-24 14:01:41.803693",
                    gtalk_id: null,
                    dob: null,
                    groups: null,
                    facebook_id: null,
                    twitter_handle: null,
                    email_address: null,
                    name: "Rodney"
                };

                api.add_contact(dummy_contact);

                fixtures.forEach(function (f) {
                    api.load_http_fixture(f);
                });
            },
            async: true
        });
    });

    var assert_summary_equal = function(summary) {
        function teardown(api, saved_user) {
            assert.deepEqual(saved_user.custom.summary, summary);
        }
        return teardown;
    };

    it("I should be asked to register", function (done) {
        var p = tester.check_state({
            user: null,
            content: null,
            next_state: "registration_start",
            response: "^Welcome to LimaLinks.[^]" +
                "In order to use this system we need to register you with a few short questions.[^]" +
                "1. Register for LimaLinks$"
        });
        p.then(done, done);
    });

    it("I should be asked for first name", function (done) {
        var p = tester.check_state({
            user: {current_state: "registration_start"},
            content: "1",
            next_state: "registration_name_first",
            response: "^Please enter your first name$"
        });
        p.then(done, done);
    });


    it("Entering first name I should be asked for last name", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_name_first",
                answers: {
                    registration_start: "registration_name_first"
                }
            },
            content: "Bob",
            next_state: "registration_name_last",
            response: "^Please enter your last name$"
        });
        p.then(done, done);
    });

    it("Entering last name I should be asked for gender", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_name_last",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob"
                }
            },
            content: "Marley",
            next_state: "registration_gender",
            response: "^What is your gender\\?[^]" +
            "1. Male[^]" +
            "2. Female$"
        });
        p.then(done, done);
    });

    it("Entering gender I should be asked for district", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_gender",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M"
                }
            },
            content: "1",
            next_state: "registration_district",
            response: "^In what district is your farm\\?$"
        });
        p.then(done, done);
    });

    it("Entering bad district I should be asked for district again", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M"
                }
            },
            content: "four",
            next_state: "registration_district",
            response: "^Sorry we could not find a matching district. Please retry entering " +
                            "what district your farm is in:$"
        });
        p.then(done, done);
    });

    it("Entering good district I should be asked for confirmation", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M"
                }
            },
            content: "three",
            next_state: "registration_district_confirm",
            response: "^Do you mean:[^]" +
                        "1. district three$"
        });
        p.then(done, done);
    });

    it("Entering good district but not unique district I should be asked for confirmation", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M"
                }
            },
            content: "district",
            next_state: "registration_district_confirm",
            response: "^Do you mean:[^]" +
                        "1. district one[^]" +
                        "2. district two[^]" +
                        "3. district three$"
        });
        p.then(done, done);
    });

    it("Confirming district I should be asked for crop", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_district_confirm",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_district: "one"
                }
            },
            content: "1",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Beans[^]" +
                        "2. Cabbage[^]" +
                        "3. Carrots[^]" +
                        "4. Cassava[^]" +
                        "5. Cauliflower[^]" +
                        "6. Chinese Cabbage[^]" +
                        "7. Coffee[^]" +
                        "8. Eggplant[^]" +
                        "9. More$"
        });
        p.then(done, done);
    });

    it("Choosing more option on crop should show more", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_district: "one",
                    registration_district_confirm: 1
                }
            },
            content: "9",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Fruit[^]" +
                        "2. Green Maize[^]" +
                        "3. Green Pepper[^]" +
                        "4. Impwa[^]" +
                        "5. Kalembula[^]" +
                        "6. Maize[^]" +
                        "7. Millet[^]" +
                        "8. Okra[^]" +
                        "9. More[^]" +
                        "10. Back$"
        });
        p.then(done, done);
    });

    it("Choosing more again option on crop should show more again", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_district: "one",
                    registration_district_confirm: 1
                },
                pages: {
                    registration_crop: 8
                }
            },
            content: "9",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Onion[^]" +
                        "2. Pumpkin Leaves[^]" +
                        "3. Rape[^]" +
                        "4. Rice[^]" +
                        "5. Soybean[^]" +
                        "6. Sugar Cane[^]" +
                        "7. Sunflowers[^]" +
                        "8. Tobacco[^]" +
                        "9. More[^]" +
                        "10. Back$"
        });
        p.then(done, done);
    });

    it("Choosing more again option for the third time on crop should show more again", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_district: "one",
                    registration_district_confirm: 1
                },
                pages: {
                    registration_crop: 16
                }
            },
            content: "9",
            next_state: "registration_crop",
            response: "^What crops do you grow\\?[^]" +
                        "1. Tomato[^]" +
                        "2. Wheat[^]" +
                        "3. Fruit - Oranges[^]" +
                        "4. Fruit - Apples[^]" +
                        "5. Fruit - Bananas[^]" +
                        "6. Back$"
        });
        p.then(done, done);
    });

    it("Choosing tomato should should ask if want to add more or finish", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_district: "one",
                    registration_district_confirm: 1
                },
                pages: {
                    registration_crop: 24
                }
            },
            content: "1",
            next_state: "registration_crop_more",
            response: "^Would you like to add another crop\\?[^]" +
                        "1. Yes[^]" +
                        "2. No$"
        });
        p.then(done, done);
    });

    it("Choosing no more crops to add I should be thanked and exit", function (done) {
        var p = tester.check_state({
            user: {
                current_state: "registration_crop_more",
                answers: {
                    registration_start: "registration_name_first",
                    registration_name_first: "Bob",
                    registration_name_last: "Marley",
                    registration_gender: "M",
                    registration_district: "one",
                    registration_district_confirm: 1,
                    registration_crop: "registration_crop_more"
                },
                custom: {
                    registration_crops: [18]
                },
                pages: {
                    registration_crop: 24
                }
            },
            content: "2",
            next_state: "registration_end",
            response: "^Thank you for registering with LimaLinks!$",
            continue_session: false
        });
        p.then(done, done);
    });

    it("Choosing to add more crops to add I return to crop list", function (done) {
            var p = tester.check_state({
                user: {
                    current_state: "registration_crop_more",
                    answers: {
                        registration_start: "registration_name_first",
                        registration_name_first: "Bob",
                        registration_name_last: "Marley",
                        registration_gender: "M",
                        registration_district: "one",
                        registration_district_confirm: 1,
                        registration_crop: "registration_crop_more"
                    },
                    custom: {
                        registration_crops: [18]
                    },
                    pages: {
                        registration_crop: 24
                    }
                },
                content: "1",
                next_state: "registration_crop",
                response: "^What crops do you grow\\?[^]" +
                        "1. Beans[^]" +
                        "2. Cabbage[^]" +
                        "3. Carrots[^]" +
                        "4. Cassava[^]" +
                        "5. Cauliflower[^]" +
                        "6. Chinese Cabbage[^]" +
                        "7. Coffee[^]" +
                        "8. Eggplant[^]" +
                        "9. More$"
            });
            p.then(done, done);
        });

});


describe("As a registered farmer", function() {

    var fixtures = test_fixtures_full;
    beforeEach(function() {
        tester = new vumigo.test_utils.ImTester(app.api, {
            custom_setup: function (api) {
                api.config_store.config = JSON.stringify({
                    lima_links_api: {
                        url: "http://qa/api/v1/",
                        username: "test",
                        password: "password",
                    }
                });

                var dummy_contact = {
                    key: "f953710a2472447591bd59e906dc2c26",
                    surname: "Trotter",
                    user_account: "test-0-user",
                    bbm_pin: null,
                    msisdn: "+1234567",
                    created_at: "2013-04-24 14:01:41.803693",
                    gtalk_id: null,
                    dob: null,
                    groups: null,
                    facebook_id: null,
                    twitter_handle: null,
                    email_address: null,
                    name: "Rodney"
                };

                api.add_contact(dummy_contact);
                api.update_contact_extras(dummy_contact, {
                    magri_id: 2
                });

                fixtures.forEach(function (f) {
                    api.load_http_fixture(f);
                });
            },
            async: true
        });
    });

    var assert_summary_equal = function(summary) {
        function teardown(api, saved_user) {
            assert.deepEqual(saved_user.custom.summary, summary);
        }
        return teardown;
    };

    it("first I should be greeted and shown menu", function(done) {
        var p = tester.check_state({
            user: {current_state: "select_service"},
            content: null,
            next_state: "select_service",
            response: ("^Hi Farmer Bob.[^]" +
                       "Select a service:[^]" +
                       "1. Market prices$")
        });
        p.then(done, done);
    });
    it("selecting market prices should ask for crop choice from my crops", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_service"
            },
            content: "1",
            next_state: "select_crop",
            response: ("^Select a crop:[^]" +
                       "1. Beans[^]" +
                       "2. Cabbage[^]" +
                       "3. Carrots[^]" +
                       "4. Cassava[^]" +
                       "5. Cauliflower[^]" +
                       "6. Chinese Cabbage[^]" +
                       "7. Coffee[^]" +
                       "8. Eggplant[^]" +
                       "9. More$")
        });
        p.then(done, done);
    });

    it("selecting more should ask for crop choice from full crop list", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_crop"
            },
            content: "9",
            next_state: "select_crop",
            response: "^Select a crop:[^]" +
                        "1. Fruit[^]" +
                        "2. Green Maize[^]" +
                        "3. Green Pepper[^]" +
                        "4. Impwa[^]" +
                        "5. Kalembula[^]" +
                        "6. Maize[^]" +
                        "7. Millet[^]" +
                        "8. Okra[^]" +
                        "9. More[^]" +
                        "10. Back$"
        });
        p.then(done, done);
    });

    it("choosing beans from crop choice should ask which markets for", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_crop",
                answers: {
                    select_service: 'select_crop'
                }
            },
            content: "1",
            next_state: "select_market_list",
            response: ("^Select which markets to view:[^]" +
                       "1. All markets[^]" +
                       "2. Best market for Beans$")
        });
        p.then(done, done);
    });
    it("choosing best market should show best market options", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market_list",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 1,
                    select_market_list: "all_markets"
                },
                custom: {
                    chosen_crop_name: "Beans",
                    chosen_markets: null
                }
            },
            content: "2",
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                       "1. Kitwe$")
        });
        p.then(done, done);
    });
    it("choosing all markets should show page 1 of all market options", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market_list",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 1,
                    select_market_list: "all_markets"
                },
                custom: {
                    chosen_crop_name: "Beans",
                    chosen_markets: null
                }
            },
            content: "1",
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                        "1. Kitwe[^]" +
                        "2. Ndola[^]" +
                        "3. Masala[^]" +
                        "4. DummyMarket4[^]" +
                        "5. DummyMarket5[^]" +
                        "6. More$")
        });
        p.then(done, done);
    });
    it("choosing More should show page 2 of all market options", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 1,
                    select_market_list: "all_markets"
                },
                custom: {
                    chosen_crop_name: "Beans",
                    chosen_markets: null
                }
            },
            content: "6",
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                        "1. DummyMarket6[^]" +
                        "2. DummyMarket7[^]" +
                        "3. DummyMarket8[^]" +
                        "4. DummyMarket9[^]" +
                        "5. Back$")
        });
        p.then(done, done);
    });
    it("selecting Kitwe for market should show prices for beans", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 1,
                    select_market_list: "all_markets"
                },
                custom: {
                    chosen_markets: [
                        [10, "Kitwe"],
                        [8, "Ndola"]
                    ],
                    chosen_crop_name: "Beans"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Beans in Kitwe:[^]" +
                       "  Big Bags: 65.00[^]" +
                       "  Bags: 30.33[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to select another crop\\.$"),
            teardown: assert_summary_equal({
                "Beans, Big Bags": { "Kitwe": "65.00" },
                "Beans, Bags": { "Kitwe": "30.33" }
            })
        });
        p.then(done, done);
    });
    it("select_market should explain if selected market has no prices", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 2,
                    select_market_list: "all_markets"
                },
                custom: {
                    chosen_markets: [
                        [10, "Kitwe"],
                        [8, "Ndola"]
                    ],
                    chosen_crop_name: "Cabbage"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Cabbage in Kitwe:[^]" +
                       "  No prices available\\.[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to select another crop\\.$"),
            teardown: assert_summary_equal(undefined)
        });
        p.then(done, done);
    });
    it("selecting 1 to see next market should show prices", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "show_prices",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 1,
                    select_market_list: "all_markets"
                },
                pages: {
                    show_prices: 0
                },
                custom: {
                    chosen_markets: [
                        [10, "Kitwe"],
                        [8, "Ndola"]
                    ],
                    chosen_crop_name: "Beans",
                    chosen_market_idx: 0,
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Beans in Ndola:[^]" +
                       "  Big Bags: 10.00[^]" +
                       "  Bags: 30.33[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to select another crop\\.$")
        });
        p.then(done, done);
    });
    it("show_prices should move to next market on 2", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "show_prices",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 1,
                    select_market_list: "all_markets"
                },
                pages: {
                    show_prices: 1
                },
                custom: {
                    chosen_markets: [
                        [10, "Kitwe"],
                        [8, "Ndola"]
                    ],
                    chosen_crop_name: "Beans",
                    chosen_market_idx: 0,
                }
            },
            content: "2",
            next_state: "show_prices",
            response: ("^Prices of Beans in Kitwe:[^]" +
                       "  Big Bags: 65.00[^]" +
                       "  Bags: 30.33[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to select another crop\\.$"),
        });
        p.then(done, done);
    });
    it("Selecting 0 should show select crop page", function(done) {
        var p = tester.check_state({
            user: {
                current_state: "show_prices",
                answers: {
                    select_service: 'select_crop',
                    select_crop: 1,
                    select_market_list: "all_markets"
                },
                pages: {
                    show_prices: 1
                },
                custom: {
                    chosen_markets: [
                        [10, "Kitwe"],
                        [8, "Ndola"]
                    ],
                    chosen_crop_name: "Beans"
                }
            },
            content: "0",
            next_state: "select_crop",
            response: ("^Select a crop:[^]" +
                       "1. Beans[^]" +
                       "2. Cabbage[^]" +
                       "3. Carrots[^]" +
                       "4. Cassava[^]" +
                       "5. Cauliflower[^]" +
                       "6. Chinese Cabbage[^]" +
                       "7. Coffee[^]" +
                       "8. Eggplant[^]" +
                       "9. More$")
        });
        p.then(done, done);
    });
    // it("Selecting 0 to exit should say goodbye", function(done) {
    //     var p = tester.check_state({
    //         user: {
    //             current_state: "show_prices",
    //             answers: {
    //                 select_service: 'select_crop',
    //                 select_crop: 1,
    //                 select_market_list: "all_markets"
    //             },
    //             pages: {
    //                 show_prices: 1
    //             },
    //             custom: {
    //                 chosen_markets: [
    //                     [10, "Kitwe"],
    //                     [8, "Ndola"]
    //                 ],
    //                 chosen_crop_name: "Beans"
    //             }
    //         },
    //         content: "0",
    //         next_state: "end",
    //         continue_session: false,
    //         response: ("^Goodbye!")
    //     });
    //     p.then(done, done);
    // });
});

describe("test sms sending", function() {
    var fixtures = test_fixtures_full;
    beforeEach(function() {
        tester = new vumigo.test_utils.ImTester(app.api, {
            custom_setup: function (api) {
                api.config_store.config = JSON.stringify({
                    sms_tag: ["pool", "tag123"],
                    lima_links_api: {
                        url: "http://qa/api/v1/",
                        username: "test",
                        password: "password",
                    }
                });

                var dummy_contact = {
                    key: "f953710a2472447591bd59e906dc2c26",
                    surname: "Trotter",
                    user_account: "test-0-user",
                    bbm_pin: null,
                    msisdn: "+1234567",
                    created_at: "2013-04-24 14:01:41.803693",
                    gtalk_id: null,
                    dob: null,
                    groups: null,
                    facebook_id: null,
                    twitter_handle: null,
                    email_address: null,
                    name: "Rodney"
                };

                api.add_contact(dummy_contact);

                fixtures.forEach(function (f) {
                    api.load_http_fixture(f);
                });
            },
            custom_teardown: function (api) {
                assert.ok(api.outbound_sends.every(
                    function (send) {
                        return (send.tagpool == "pool" &&
                                send.tag == "tag123" &&
                                send.to_addr == "1234567");
                    }
                ));
            },
            async: true
        });
    });

    var assert_single_sms = function(content) {
        var teardown = function(api) {
            var sms = api.outbound_sends[0];
            assert.equal(api.outbound_sends.length, 1);
            assert.equal(sms.content, content);
        };
        return teardown;
    };

    var assert_no_sms = function() {
        var teardown = function(api) {
            assert.equal(api.outbound_sends.length, 0);
        };
        return teardown;
    };

    var get_user = function() {
        return {
            current_state: "show_prices",
            custom: {
                chosen_markets: [
                    ["market1", "Kitwe"],
                    ["market2", "Ndola"]
                ],
                chosen_market_idx: 0,
                chosen_crop_name: "Peas"
            }
        };
    };

    it("should not sms summary if no prices present", function (done) {
        var p = tester.check_state({
            user: get_user(),
            content: "0",
            next_state: "select_crop",
            response: ("^Select a crop:[^]" +
                       "1. Beans[^]" +
                       "2. Cabbage[^]" +
                       "3. Carrots[^]" +
                       "4. Cassava[^]" +
                       "5. Cauliflower[^]" +
                       "6. Chinese Cabbage[^]" +
                       "7. Coffee[^]" +
                       "8. Eggplant[^]" +
                       "9. More$"),
            teardown: assert_no_sms()
        });
        p.then(done, done);
    });

    it("should sms summary if prices present", function (done) {
        var user = get_user();
        user.custom.summary = {
            "Peas, boxes": {
                "Kitwe": "15000",
                "Ndola": "15500"
            },
            "Peas, crates": {
                "Kitwe": "16000"
            }
        };
        var p = tester.check_state({
            user: user,
            content: "0",
            next_state: "select_crop",
            response: ("^Select a crop:[^]" +
                       "1. Beans[^]" +
                       "2. Cabbage[^]" +
                       "3. Carrots[^]" +
                       "4. Cassava[^]" +
                       "5. Cauliflower[^]" +
                       "6. Chinese Cabbage[^]" +
                       "7. Coffee[^]" +
                       "8. Eggplant[^]" +
                       "9. More$"),
            teardown: assert_single_sms(
                "Peas, boxes: Ndola K15500, Kitwe K15000\n" +
                "Peas, crates: Kitwe K16000"
            )
        });
        p.then(done, done);
    });
});
