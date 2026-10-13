---
type: Page
description: "The shop, every class in its group, drawn one crossing at a time: checkout, recommend."
---

Every box is a class in the page its group names, and the group's number is its file's slot. An edge reads tail to head: `held by` is a field, `constructs` is `model_validate` by shared names, `returns` is an interpreter's `interpret`. What differs between the variants of a union is one derivation, under one name, on each variant.

## Checkout

```mermaid
flowchart LR
    subgraph s1["1 ordered union · collection"]
        StatedReason["StatedReason: DeclineReason, else UnlistedReason"]
        StatedError["StatedError: ProviderError, else UnlistedError"]
        DeclineReasons["DeclineReasons"]
    end

    subgraph s2["2 foreign model"]
        DiscountAddress["DiscountAddress: customer"]
        DiscountOffer["DiscountOffer: percent"]
        CardCharge["CardCharge: amt · cur · src · ref"]
        ChargeApproved["ChargeApproved: id"]
        ChargeDeclined["ChargeDeclined: decline_codes"]
        ChargeFailed["ChargeFailed: error"]
        ChargeReply["ChargeReply"]
    end

    subgraph s2p["4 provider"]
        Promotions["Promotions: url"]
        CardPayments["CardPayments: provider · url · key"]
        InvoicePayments["InvoicePayments: provider · url"]
        Payments["Payments"]
    end

    subgraph s3["3 value object · collection"]
        Line["Line: sku · unit_price · quantity"]
        Lines["Lines"]
        Discount["Discount: percent"]
        Approval["Approval: charge"]
        Decline["Decline: reasons"]
        Failure["Failure: error"]
    end

    subgraph s5c["5 concept model"]
        Order["Order: id · customer · card · currency · lines"]
        PricedOrder["PricedOrder: order · discount"]
    end

    subgraph s5u["5 union"]
        PaidOrder["PaidOrder: order · payment"]
        DeclinedOrder["DeclinedOrder: order · payment"]
        UnsettledOrder["UnsettledOrder: order · payment"]
        OrderOutcome["OrderOutcome"]
    end

    subgraph s5a["5 action"]
        ReadDiscount["ReadDiscount: order"]
        Charge["Charge: order"]
    end

    subgraph s6["6 contract model"]
        PublishedOrder["PublishedOrder: id · amount · currency · discount"]
        OrderConfirmed["OrderConfirmed: order · payment"]
        OrderRejected["OrderRejected: order · payment"]
        OrderUnsettled["OrderUnsettled: order · payment"]
        OrderReply["OrderReply"]
    end

    subgraph s7["7 config"]
        ShopConfig["ShopConfig: promotions · payments · catalog · recommending"]
    end

    subgraph s8["8 transformation"]
        ChargeAttempt["ChargeAttempt: order · reply"]
    end

    subgraph s9["9 effect interpreter"]
        ReadDiscountInterpreter["ReadDiscountInterpreter: action · provider"]
        ChargeInterpreter["ChargeInterpreter: action · provider"]
    end

    subgraph s10["10 route"]
        CheckoutRoute["CheckoutRoute: order"]
        ReplyRoute["ReplyRoute: outcome"]
    end

    StatedReason -->|held by| DeclineReasons
    DeclineReasons -->|held by| ChargeDeclined
    DeclineReasons -->|held by| Decline
    StatedError -->|held by| ChargeFailed
    StatedError -->|held by| Failure
    Line -->|held by| Lines
    Lines -->|held by| Order
    Order -->|held by| CheckoutRoute
    Order -->|held by| ReadDiscount
    ReadDiscount -->|held by| ReadDiscountInterpreter
    ReadDiscountInterpreter ==>|returns| PricedOrder
    Order -.->|constructs| DiscountAddress
    DiscountOffer -.->|constructs| Discount
    Order -->|held by| PricedOrder
    Discount -->|held by| PricedOrder
    PricedOrder -->|held by| Charge
    Charge -->|held by| ChargeInterpreter
    ChargeInterpreter ==>|returns| ChargeAttempt
    PricedOrder -.->|constructs| CardCharge
    PricedOrder -->|held by| ChargeAttempt
    ChargeApproved -->|held by| ChargeReply
    ChargeDeclined -->|held by| ChargeReply
    ChargeFailed -->|held by| ChargeReply
    ChargeReply -->|held by| ChargeAttempt
    ChargeApproved -.->|constructs| Approval
    ChargeDeclined -.->|constructs| Decline
    ChargeFailed -.->|constructs| Failure
    Approval -->|held by| PaidOrder
    Decline -->|held by| DeclinedOrder
    Failure -->|held by| UnsettledOrder
    PaidOrder -->|held by| OrderOutcome
    DeclinedOrder -->|held by| OrderOutcome
    UnsettledOrder -->|held by| OrderOutcome
    ChargeAttempt -.->|constructs| OrderOutcome
    PricedOrder -.->|constructs| PublishedOrder
    Discount -->|held by| PublishedOrder
    PublishedOrder -->|held by| OrderConfirmed
    PublishedOrder -->|held by| OrderRejected
    PublishedOrder -->|held by| OrderUnsettled
    PaidOrder -.->|constructs| OrderConfirmed
    DeclinedOrder -.->|constructs| OrderRejected
    UnsettledOrder -.->|constructs| OrderUnsettled
    OrderConfirmed -->|held by| OrderReply
    OrderRejected -->|held by| OrderReply
    OrderUnsettled -->|held by| OrderReply
    OrderOutcome -.->|constructs| OrderReply
    OrderReply -->|held by| ReplyRoute
    CardPayments -->|held by| Payments
    InvoicePayments -->|held by| Payments
    Promotions -->|held by| ShopConfig
    Payments -->|held by| ShopConfig
    Promotions -->|held by| ReadDiscountInterpreter
    Payments -->|held by| ChargeInterpreter
```

## Recommend

```mermaid
flowchart LR
    subgraph s2["2 foreign model"]
        CatalogPoint["CatalogPoint: sku"]
        IndexQuery["IndexQuery: query · filter · score_threshold · group_size · limit"]
        PointHit["PointHit: id · score · payload"]
        Hits["Hits"]
        PointGroup["PointGroup: hits · id"]
        PointGroups["PointGroups"]
        GroupResult["GroupResult: groups"]
        IndexGroups["IndexGroups: result · status · time"]
        IndexFailure["IndexFailure: status · time"]
        IndexReply["IndexReply"]
    end

    subgraph s2p["4 provider"]
        CatalogIndex["CatalogIndex: url"]
    end

    subgraph s3["3 value object · collection"]
        Line["Line: sku · unit_price · quantity"]
        Recommending["Recommending: closeness · per_aisle · limit"]
        Match["Match: sku · category · similarity"]
        RelatedMatches["RelatedMatches: one or more"]
        NoMatches["NoMatches: none"]
    end

    subgraph s5c["5 concept model"]
        RecommendedOrder["RecommendedOrder: order · recommendation"]
    end

    subgraph s5u["5 union"]
        PaidOrder["PaidOrder: order · payment"]
        Recommended["Recommended: matches"]
        NothingRelated["NothingRelated: matches"]
        Unavailable["Unavailable: reason"]
        Recommendation["Recommendation"]
    end

    subgraph s5a["5 action"]
        FindRelated["FindRelated: order · tuning"]
    end

    subgraph s7["7 config"]
        ShopConfig["ShopConfig: promotions · payments · catalog · recommending"]
    end

    subgraph s8["8 transformation"]
        RelatedQuery["RelatedQuery: action"]
        RelatedSearch["RelatedSearch: order · reply"]
    end

    subgraph s9["9 effect interpreter"]
        FindRelatedInterpreter["FindRelatedInterpreter: action · provider"]
    end

    PaidOrder -->|held by| FindRelated
    FindRelated -->|held by| FindRelatedInterpreter
    FindRelatedInterpreter ==>|returns| RelatedSearch
    FindRelated -->|held by| RelatedQuery
    RelatedQuery -.->|constructs| IndexQuery
    Line -.->|constructs| CatalogPoint
    PointHit -->|held by| Hits
    Hits -->|held by| PointGroup
    PointGroup -->|held by| PointGroups
    PointGroups -->|held by| GroupResult
    GroupResult -->|held by| IndexGroups
    IndexGroups -->|held by| IndexReply
    IndexFailure -->|held by| IndexReply
    PaidOrder -->|held by| RelatedSearch
    IndexReply -->|held by| RelatedSearch
    PointHit -.->|constructs| Match
    Match -->|held by| RelatedMatches
    Match -->|held by| NoMatches
    IndexGroups -.->|constructs| Recommended
    IndexGroups -.->|constructs| NothingRelated
    IndexFailure -.->|constructs| Unavailable
    RelatedMatches -->|held by| Recommended
    NoMatches -->|held by| NothingRelated
    Recommended -->|held by| Recommendation
    NothingRelated -->|held by| Recommendation
    Unavailable -->|held by| Recommendation
    RelatedSearch -.->|constructs| RecommendedOrder
    PaidOrder -->|held by| RecommendedOrder
    Recommendation -->|held by| RecommendedOrder
    Recommending -->|held by| FindRelated
    CatalogIndex -->|held by| ShopConfig
    CatalogIndex -->|held by| FindRelatedInterpreter
    Recommending -->|held by| ShopConfig
```
