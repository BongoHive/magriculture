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


describe("test menu worker", function() {
    var tester = new test_utils.ImTester(app.api, {
        max_response_length: 160
    });

    var assert_summary_equal = function(summary) {
        function teardown(api, saved_user) {
            assert.deepEqual(saved_user.custom.summary, summary);
        }
        return teardown;
    };

    it("new users should see the select_service state", function () {
        tester.check_state({
            user: null,
            content: null,
            next_state: "select_service",
            response: "^Hi Farmer Bob."
        });
    });
    it("select_service state should respond", function() {
        tester.check_state({
            user: {current_state: "select_service"},
            content: null,
            next_state: "select_service",
            response: ("^Hi Farmer Bob.[^]" +
                       "Select a service:[^]" +
                       "1. Market prices$")
        });
    });
    it("select_crop should respond", function() {
        tester.check_state({
            user: {current_state: "select_crop"},
            content: null,
            next_state: "select_crop",
            response: ("^Select a crop:[^]" +
                       "1. Peas[^]" +
                       "2. Carrots$")
        });
    });
    it("select_market_list should respond", function() {
        tester.check_state({
            user: {
                current_state: "select_market_list",
                custom: {
                    chosen_crop_name: "Peas"
                }
            },
            content: null,
            next_state: "select_market_list",
            response: ("^Select which markets to view:[^]" +
                       "1. All markets[^]" +
                       "2. Best markets for Peas$")
        });
    });
    it("select_market should respond (best_markets)", function() {
        tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_crop: "crop1",
                    select_market_list: "best_markets"
                }
            },
            content: null,
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                       "1. Kitwe[^]" +
                       "2. Ndola$")
        });
    });
    it("select_market should respond (all_markets)", function() {
        tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_market_list: "all_markets"
                }
            },
            content: null,
            next_state: "select_market",
            response: ("^Select a market:[^]" +
                       "1. Kitwe[^]" +
                       "2. Ndola[^]" +
                       "3. Masala$")
        });
    });
    it("select_market should show_prices for selected market", function() {
        tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_crop: "crop1"
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_crop_name: "Peas"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Peas in Kitwe:[^]" +
                       "  boxes: 1.27[^]" +
                       "  crates: 1.70[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$"),
            teardown: assert_summary_equal({
                "Peas, boxes": { "Kitwe": "1.27" },
                "Peas, crates": { "Kitwe": "1.70" }
            })
        });
    });
    it("select_market should explain if selected market has no prices", function() {
        tester.check_state({
            user: {
                current_state: "select_market",
                answers: {
                    select_crop: "crop2"
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_crop_name: "Carrots"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Carrots in Kitwe:[^]" +
                       "  No prices available\\.[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$"),
            teardown: assert_summary_equal(undefined)
        });
    });
    it("show_prices should move to previous market on 1", function() {
        tester.check_state({
            user: {
                current_state: "show_prices",
                answers: {
                    select_crop: "crop1"
                },
                pages: {
                    show_prices: 0
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_market_idx: 0,
                    chosen_crop_name: "Peas"
                }
            },
            content: "1",
            next_state: "show_prices",
            response: ("^Prices of Peas in Ndola:[^]" +
                       "  boxes: -[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$")
        });
    });
    it("show_prices should move to next market on 2", function() {
        tester.check_state({
            user: {
                current_state: "show_prices",
                answers: {
                    select_crop: "crop1"
                },
                pages: {
                    show_prices: 1
                },
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_market_idx: 0,
                    chosen_crop_name: "Peas"
                }
            },
            content: "2",
            next_state: "show_prices",
            response: ("^Prices of Peas in Kitwe:[^]" +
                       "  boxes: 1.27[^]" +
                       "  crates: 1.70[^]" +
                       "Enter 1 for next market, 2 for previous market\\.[^]" +
                       "Enter 0 to exit\\.$")
        });
    });
    it("show_prices should move to end on 0", function() {
        tester.check_state({
            user: {
                current_state: "show_prices",
                custom: {
                    chosen_markets: [
                        ["market1", "Kitwe"],
                        ["market2", "Ndola"]
                    ],
                    chosen_market_idx: 0,
                    chosen_crop_name: "Peas"
               }
            },
            content: "0",
            next_state: "end",
            continue_session: false,
            response: ("^Goodbye!")
        });
    });
});

describe("test sms sending", function() {
    var tester = new test_utils.ImTester(app.api, {
        max_response_length: 160,
        custom_setup: function (api) {
            api.config_store.config = JSON.stringify({
                sms_tag: ["pool", "tag123"]
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
        }
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

    it("should not sms summary if no prices present", function () {
        tester.check_state({
            user: get_user(),
            content: "0",
            next_state: "end",
            continue_session: false,
            response: ("^Goodbye!"),
            teardown: assert_no_sms()
        });
    });

    it("should sms summary if prices present", function () {
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
        tester.check_state({
            user: user,
            content: "0",
            next_state: "end",
            continue_session: false,
            response: ("^Goodbye!"),
            teardown: assert_single_sms(
                "Peas, boxes: Ndola K15500, Kitwe K15000\n" +
                "Peas, crates: Kitwe K16000"
            )
        });
    });
});
