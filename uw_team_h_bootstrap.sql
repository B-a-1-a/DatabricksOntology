%sql
-- Bootstrap catalog + schemas + tables for ontology crawling in Databricks
-- Source datasets: samples.tpcds_sf1 and samples.wanderbricks
-- Target catalog: uw_team_h
--
-- Notes:
-- 1) Assumes you have permissions to create/use the target catalog and schemas.
-- 2) Uses CREATE OR REPLACE TABLE AS SELECT to materialize copies from the built-in samples catalog.
-- 3) Adds comments to the catalog, schemas, selected raw tables, and curated feature tables.

-- COMMENT ON CATALOG uw_team_h IS 'Sandbox catalog for ontology crawling, feature discovery, and agent traversal experiments.';

USE CATALOG uw_team_h;

CREATE SCHEMA IF NOT EXISTS uw_team_h.retail_dimensions
  COMMENT 'Retail reference and dimension tables copied from samples.tpcds_sf1.';

CREATE SCHEMA IF NOT EXISTS uw_team_h.retail_facts
  COMMENT 'Retail fact and event tables copied from samples.tpcds_sf1.';

CREATE SCHEMA IF NOT EXISTS uw_team_h.travel_entities
  COMMENT 'Travel marketplace entity tables copied from samples.wanderbricks.';

CREATE SCHEMA IF NOT EXISTS uw_team_h.travel_events
  COMMENT 'Travel marketplace event, transaction, and behavioral tables copied from samples.wanderbricks.';

CREATE SCHEMA IF NOT EXISTS uw_team_h.agent_features
  COMMENT 'Curated, semantically rich feature tables intended to help ontology and feature-recommendation agents.';

-- ---------------------------------------------------------------------
-- TPC-DS reference / dimension tables
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.call_center            AS SELECT * FROM samples.tpcds_sf1.call_center;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.catalog_page           AS SELECT * FROM samples.tpcds_sf1.catalog_page;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.customer               AS SELECT * FROM samples.tpcds_sf1.customer;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.customer_address       AS SELECT * FROM samples.tpcds_sf1.customer_address;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.customer_demographics  AS SELECT * FROM samples.tpcds_sf1.customer_demographics;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.date_dim               AS SELECT * FROM samples.tpcds_sf1.date_dim;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.household_demographics AS SELECT * FROM samples.tpcds_sf1.household_demographics;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.income_band            AS SELECT * FROM samples.tpcds_sf1.income_band;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.item                   AS SELECT * FROM samples.tpcds_sf1.item;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.promotion              AS SELECT * FROM samples.tpcds_sf1.promotion;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.reason                 AS SELECT * FROM samples.tpcds_sf1.reason;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.ship_mode              AS SELECT * FROM samples.tpcds_sf1.ship_mode;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.store                  AS SELECT * FROM samples.tpcds_sf1.store;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.time_dim               AS SELECT * FROM samples.tpcds_sf1.time_dim;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.warehouse              AS SELECT * FROM samples.tpcds_sf1.warehouse;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.web_page               AS SELECT * FROM samples.tpcds_sf1.web_page;
CREATE OR REPLACE TABLE uw_team_h.retail_dimensions.web_site               AS SELECT * FROM samples.tpcds_sf1.web_site;

-- ---------------------------------------------------------------------
-- TPC-DS fact / event tables
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE uw_team_h.retail_facts.catalog_returns AS SELECT * FROM samples.tpcds_sf1.catalog_returns;
CREATE OR REPLACE TABLE uw_team_h.retail_facts.catalog_sales   AS SELECT * FROM samples.tpcds_sf1.catalog_sales;
CREATE OR REPLACE TABLE uw_team_h.retail_facts.inventory       AS SELECT * FROM samples.tpcds_sf1.inventory;
CREATE OR REPLACE TABLE uw_team_h.retail_facts.store_returns   AS SELECT * FROM samples.tpcds_sf1.store_returns;
CREATE OR REPLACE TABLE uw_team_h.retail_facts.store_sales     AS SELECT * FROM samples.tpcds_sf1.store_sales;
CREATE OR REPLACE TABLE uw_team_h.retail_facts.web_returns     AS SELECT * FROM samples.tpcds_sf1.web_returns;
CREATE OR REPLACE TABLE uw_team_h.retail_facts.web_sales       AS SELECT * FROM samples.tpcds_sf1.web_sales;

-- ---------------------------------------------------------------------
-- Wanderbricks entity tables
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE uw_team_h.travel_entities.amenities          AS SELECT * FROM samples.wanderbricks.amenities;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.countries          AS SELECT * FROM samples.wanderbricks.countries;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.destinations       AS SELECT * FROM samples.wanderbricks.destinations;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.employees          AS SELECT * FROM samples.wanderbricks.employees;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.hosts              AS SELECT * FROM samples.wanderbricks.hosts;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.properties         AS SELECT * FROM samples.wanderbricks.properties;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.property_amenities AS SELECT * FROM samples.wanderbricks.property_amenities;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.property_images    AS SELECT * FROM samples.wanderbricks.property_images;
CREATE OR REPLACE TABLE uw_team_h.travel_entities.users              AS SELECT * FROM samples.wanderbricks.users;

-- ---------------------------------------------------------------------
-- Wanderbricks event / transaction / behavior tables
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE uw_team_h.travel_events.booking_updates        AS SELECT * FROM samples.wanderbricks.booking_updates;
CREATE OR REPLACE TABLE uw_team_h.travel_events.bookings               AS SELECT * FROM samples.wanderbricks.bookings;
CREATE OR REPLACE TABLE uw_team_h.travel_events.clickstream            AS SELECT * FROM samples.wanderbricks.clickstream;
CREATE OR REPLACE TABLE uw_team_h.travel_events.customer_support_logs  AS SELECT * FROM samples.wanderbricks.customer_support_logs;
CREATE OR REPLACE TABLE uw_team_h.travel_events.page_views             AS SELECT * FROM samples.wanderbricks.page_views;
CREATE OR REPLACE TABLE uw_team_h.travel_events.payments               AS SELECT * FROM samples.wanderbricks.payments;
CREATE OR REPLACE TABLE uw_team_h.travel_events.reviews                AS SELECT * FROM samples.wanderbricks.reviews;

-- ---------------------------------------------------------------------
-- Table comments: keep these focused on ontology traversal hints.
-- ---------------------------------------------------------------------
COMMENT ON TABLE uw_team_h.retail_dimensions.customer IS
  'Retail customer master records. Useful join hub for customer-level features across store, catalog, and web sales.';

COMMENT ON TABLE uw_team_h.retail_dimensions.item IS
  'Retail item dimension. Useful join hub for SKU-level or product-level features across sales, returns, and inventory.';

COMMENT ON TABLE uw_team_h.retail_dimensions.date_dim IS
  'Canonical retail date dimension for time-based rollups and seasonality features.';

COMMENT ON TABLE uw_team_h.retail_dimensions.store IS
  'Retail store dimension for geography and channel-specific performance features.';

COMMENT ON TABLE uw_team_h.retail_facts.store_sales IS
  'Point-of-sale sales fact table. Key source for customer spend, item demand, store performance, and time-series features.';

COMMENT ON TABLE uw_team_h.retail_facts.catalog_sales IS
  'Catalog order sales fact table. Useful for channel mix, customer propensity, and item affinity features.';

COMMENT ON TABLE uw_team_h.retail_facts.web_sales IS
  'E-commerce sales fact table. Useful for digital demand, recency-frequency-monetary analysis, and online conversion features.';

COMMENT ON TABLE uw_team_h.retail_facts.inventory IS
  'Inventory snapshots by item and warehouse/date. Useful for stockout, availability, and supply-demand features.';

COMMENT ON TABLE uw_team_h.travel_entities.users IS
  'Traveler and customer entity records. Primary entity for user-level travel features and behavioral joins.';

COMMENT ON TABLE uw_team_h.travel_entities.properties IS
  'Property listing entity records. Primary entity for property-level demand, quality, and pricing features.';

COMMENT ON TABLE uw_team_h.travel_entities.hosts IS
  'Host entity records that own or operate property listings.';

COMMENT ON TABLE uw_team_h.travel_entities.destinations IS
  'Destination lookup table referenced by property listings for location-aware travel features.';

COMMENT ON TABLE uw_team_h.travel_events.bookings IS
  'Reservation fact table with user, property, stay dates, total amount, and booking status. Primary source for conversion and revenue features.';

COMMENT ON TABLE uw_team_h.travel_events.payments IS
  'Payment records tied to bookings. Useful for payment reliability, settlement, and revenue realization features.';

COMMENT ON TABLE uw_team_h.travel_events.reviews IS
  'Post-stay review events with ratings and comments. Useful for property quality and guest satisfaction features.';

COMMENT ON TABLE uw_team_h.travel_events.clickstream IS
  'Behavioral event stream with nested metadata such as device and referrer. Useful for session, funnel, and intent features.';

COMMENT ON TABLE uw_team_h.travel_events.page_views IS
  'Page view activity for users and properties. Useful for browsing-intent and property engagement features.';

COMMENT ON TABLE uw_team_h.travel_events.customer_support_logs IS
  'Support interactions tied to users. Useful for friction, issue, and post-booking support features.';

-- ---------------------------------------------------------------------
-- Curated feature tables for the agent to discover.
-- These are intentionally simple and semantically rich.
-- ---------------------------------------------------------------------
CREATE OR REPLACE TABLE uw_team_h.agent_features.travel_user_booking_features AS
SELECT
  b.user_id,
  COUNT(*) AS total_bookings,
  SUM(CASE WHEN lower(b.status) IN ('confirmed', 'completed') THEN 1 ELSE 0 END) AS successful_bookings,
  SUM(CASE WHEN lower(b.status) IN ('cancelled', 'canceled') THEN 1 ELSE 0 END) AS cancelled_bookings,
  ROUND(SUM(b.total_amount), 2) AS gross_booking_amount,
  ROUND(AVG(b.total_amount), 2) AS avg_booking_amount,
  MIN(b.check_in) AS first_check_in_date,
  MAX(b.check_in) AS most_recent_check_in_date
FROM uw_team_h.travel_events.bookings b
GROUP BY b.user_id;

COMMENT ON TABLE uw_team_h.agent_features.travel_user_booking_features IS
  'User-level booking aggregates derived from bookings. Good candidate feature table for churn, conversion, rebooking, and customer value models.';

COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.user_id IS
  'Primary user entity key from the bookings table.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.total_bookings IS
  'Total number of bookings observed for the user.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.successful_bookings IS
  'Count of bookings with confirmed or completed status.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.cancelled_bookings IS
  'Count of bookings with canceled or cancelled status.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.gross_booking_amount IS
  'Total booked monetary value summed across all user bookings.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.avg_booking_amount IS
  'Average monetary value per booking for the user.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.first_check_in_date IS
  'Earliest observed stay start date for the user.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_user_booking_features.most_recent_check_in_date IS
  'Most recent observed stay start date for the user.';

CREATE OR REPLACE TABLE uw_team_h.agent_features.travel_property_quality_features AS
WITH booking_agg AS (
  SELECT
    property_id,
    COUNT(*) AS total_bookings,
    ROUND(SUM(total_amount), 2) AS gross_booking_amount,
    ROUND(AVG(total_amount), 2) AS avg_booking_amount
  FROM uw_team_h.travel_events.bookings
  GROUP BY property_id
),
review_agg AS (
  SELECT
    property_id,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*) AS review_count
  FROM uw_team_h.travel_events.reviews
  WHERE is_deleted = false
  GROUP BY property_id
)
SELECT
  p.property_id,
  p.title AS property_title,
  p.property_type,
  COALESCE(b.total_bookings, 0) AS total_bookings,
  COALESCE(b.gross_booking_amount, 0.0) AS gross_booking_amount,
  COALESCE(b.avg_booking_amount, 0.0) AS avg_booking_amount,
  COALESCE(r.avg_rating, 0.0) AS avg_rating,
  COALESCE(r.review_count, 0) AS review_count
FROM uw_team_h.travel_entities.properties p
LEFT JOIN booking_agg b
  ON p.property_id = b.property_id
LEFT JOIN review_agg r
  ON p.property_id = r.property_id;

COMMENT ON TABLE uw_team_h.agent_features.travel_property_quality_features IS
  'Property-level aggregates that combine booking demand and guest review quality. Good candidate feature table for ranking, pricing, and occupancy models.';

COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.property_id IS
  'Primary property entity key from the properties table.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.property_title IS
  'Human-readable property title from the properties table.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.property_type IS
  'Property classification such as apartment, house, or similar listing type.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.total_bookings IS
  'Number of bookings associated with the property.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.gross_booking_amount IS
  'Total booked monetary value across all bookings for the property.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.avg_booking_amount IS
  'Average booking amount for the property.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.avg_rating IS
  'Average rating across non-deleted reviews for the property.';
COMMENT ON COLUMN uw_team_h.agent_features.travel_property_quality_features.review_count IS
  'Number of non-deleted reviews used to compute the property rating statistics.';

-- ---------------------------------------------------------------------
-- Suggested crawl queries for your ontology service.
-- ---------------------------------------------------------------------
-- All schemas in this catalog:
-- SELECT catalog_name, schema_name, comment
-- FROM system.information_schema.schemata
-- WHERE catalog_name = 'uw_team_h'
-- ORDER BY schema_name;

-- All tables in this catalog:
-- SELECT table_catalog, table_schema, table_name, table_type, comment
-- FROM system.information_schema.tables
-- WHERE table_catalog = 'uw_team_h'
-- ORDER BY table_schema, table_name;

-- All columns in this catalog:
-- SELECT table_catalog, table_schema, table_name, column_name, data_type, full_data_type, comment
-- FROM system.information_schema.columns
-- WHERE table_catalog = 'uw_team_h'
-- ORDER BY table_schema, table_name, ordinal_position;

-- Stable single-table metadata for parsing:
-- DESCRIBE TABLE AS JSON uw_team_h.agent_features.travel_property_quality_features;
