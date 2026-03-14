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

-- Patch comments for uw_team_h.retail_channel
-- Run after the CREATE TABLE AS SELECT statements in the bootstrap.

COMMENT ON TABLE uw_team_h.retail_channel.call_center IS 'Retail call center dimension with organizational, staffing, and location attributes.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_call_center_sk COMMENT 'Surrogate key for the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_call_center_id COMMENT 'Business identifier for the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_rec_start_date COMMENT 'Record effective start date.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_rec_end_date COMMENT 'Record effective end date.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_closed_date_sk COMMENT 'Date surrogate key for when the call center closed.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_open_date_sk COMMENT 'Date surrogate key for when the call center opened.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_name COMMENT 'Call center name.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_class COMMENT 'Call center class or tier.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_employees COMMENT 'Number of employees assigned to the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_sq_ft COMMENT 'Facility square footage.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_hours COMMENT 'Operating hours string.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_manager COMMENT 'Call center manager name.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_mkt_id COMMENT 'Market identifier for the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_mkt_class COMMENT 'Market classification for the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_mkt_desc COMMENT 'Market description.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_market_manager COMMENT 'Manager responsible for the market.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_division COMMENT 'Division identifier.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_division_name COMMENT 'Division name.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_company COMMENT 'Company identifier.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_company_name COMMENT 'Company name.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_street_number COMMENT 'Street number portion of the address.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_street_name COMMENT 'Street name portion of the address.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_street_type COMMENT 'Street type portion of the address.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_suite_number COMMENT 'Suite or unit number.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_city COMMENT 'City of the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_county COMMENT 'County of the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_state COMMENT 'State or province of the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_zip COMMENT 'Postal code of the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_country COMMENT 'Country of the call center.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_gmt_offset COMMENT 'GMT offset for the location.';
ALTER TABLE uw_team_h.retail_channel.call_center ALTER COLUMN cc_tax_percentage COMMENT 'Local tax percentage for the call center location.';

COMMENT ON TABLE uw_team_h.retail_channel.catalog_page IS 'Retail catalog page dimension describing printed catalog content and lifecycle dates.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_catalog_page_sk COMMENT 'Surrogate key for the catalog page.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_catalog_page_id COMMENT 'Business identifier for the catalog page.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_start_date_sk COMMENT 'Date surrogate key for when the page became active.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_end_date_sk COMMENT 'Date surrogate key for when the page stopped being active.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_department COMMENT 'Department featured on the catalog page.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_catalog_number COMMENT 'Catalog identifier containing the page.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_catalog_page_number COMMENT 'Page number within the catalog.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_description COMMENT 'Description of the page content or layout.';
ALTER TABLE uw_team_h.retail_channel.catalog_page ALTER COLUMN cp_type COMMENT 'Catalog page type.';

COMMENT ON TABLE uw_team_h.retail_channel.date_dim IS 'Calendar and fiscal date dimension used across retail channels.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_date_sk COMMENT 'Surrogate key for the date.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_date_id COMMENT 'Business identifier for the date.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_date COMMENT 'Calendar date.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_month_seq COMMENT 'Sequential month number in the calendar.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_week_seq COMMENT 'Sequential week number in the calendar.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_quarter_seq COMMENT 'Sequential quarter number in the calendar.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_year COMMENT 'Calendar year.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_dow COMMENT 'Day of week number.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_moy COMMENT 'Month of year number.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_dom COMMENT 'Day of month number.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_qoy COMMENT 'Quarter of year number.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_fy_year COMMENT 'Fiscal year.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_fy_quarter_seq COMMENT 'Sequential fiscal quarter number.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_fy_week_seq COMMENT 'Sequential fiscal week number.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_day_name COMMENT 'Name of the day of week.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_quarter_name COMMENT 'Label for the calendar quarter.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_holiday COMMENT 'Flag indicating whether the date is a holiday.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_weekend COMMENT 'Flag indicating whether the date falls on a weekend.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_following_holiday COMMENT 'Flag indicating whether the date follows a holiday.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_first_dom COMMENT 'Flag indicating whether the date is the first day of the month.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_last_dom COMMENT 'Flag indicating whether the date is the last day of the month.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_same_day_ly COMMENT 'Surrogate key for the same calendar day last year.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_same_day_lq COMMENT 'Surrogate key for the same calendar day last quarter.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_current_day COMMENT 'Flag indicating whether the date is the current day in the benchmark.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_current_week COMMENT 'Flag indicating whether the date falls in the current week in the benchmark.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_current_month COMMENT 'Flag indicating whether the date falls in the current month in the benchmark.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_current_quarter COMMENT 'Flag indicating whether the date falls in the current quarter in the benchmark.';
ALTER TABLE uw_team_h.retail_channel.date_dim ALTER COLUMN d_current_year COMMENT 'Flag indicating whether the date falls in the current year in the benchmark.';

COMMENT ON TABLE uw_team_h.retail_channel.reason IS 'Reason dimension for returns or operational adjustments.';
ALTER TABLE uw_team_h.retail_channel.reason ALTER COLUMN r_reason_sk COMMENT 'Surrogate key for the return or adjustment reason.';
ALTER TABLE uw_team_h.retail_channel.reason ALTER COLUMN r_reason_id COMMENT 'Business identifier for the reason.';
ALTER TABLE uw_team_h.retail_channel.reason ALTER COLUMN r_reason_desc COMMENT 'Description of the reason.';

COMMENT ON TABLE uw_team_h.retail_channel.ship_mode IS 'Shipping mode dimension with carrier and contract details.';
ALTER TABLE uw_team_h.retail_channel.ship_mode ALTER COLUMN sm_ship_mode_sk COMMENT 'Surrogate key for the shipping mode.';
ALTER TABLE uw_team_h.retail_channel.ship_mode ALTER COLUMN sm_ship_mode_id COMMENT 'Business identifier for the shipping mode.';
ALTER TABLE uw_team_h.retail_channel.ship_mode ALTER COLUMN sm_type COMMENT 'Shipping mode type.';
ALTER TABLE uw_team_h.retail_channel.ship_mode ALTER COLUMN sm_code COMMENT 'Short code for the shipping mode.';
ALTER TABLE uw_team_h.retail_channel.ship_mode ALTER COLUMN sm_carrier COMMENT 'Shipping carrier name.';
ALTER TABLE uw_team_h.retail_channel.ship_mode ALTER COLUMN sm_contract COMMENT 'Carrier contract identifier or description.';

COMMENT ON TABLE uw_team_h.retail_channel.store IS 'Retail store dimension with staffing, geography, and address attributes.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_store_sk COMMENT 'Surrogate key for the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_store_id COMMENT 'Business identifier for the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_rec_start_date COMMENT 'Record effective start date.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_rec_end_date COMMENT 'Record effective end date.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_closed_date_sk COMMENT 'Date surrogate key for when the store closed.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_store_name COMMENT 'Store name.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_number_employees COMMENT 'Number of employees assigned to the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_floor_space COMMENT 'Store floor space in square feet.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_hours COMMENT 'Store operating hours string.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_manager COMMENT 'Store manager name.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_market_id COMMENT 'Market identifier for the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_geography_class COMMENT 'Geography classification for the store location.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_market_desc COMMENT 'Market description.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_market_manager COMMENT 'Manager responsible for the market.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_division_id COMMENT 'Division identifier.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_division_name COMMENT 'Division name.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_company_id COMMENT 'Company identifier.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_company_name COMMENT 'Company name.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_street_number COMMENT 'Street number portion of the address.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_street_name COMMENT 'Street name portion of the address.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_street_type COMMENT 'Street type portion of the address.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_suite_number COMMENT 'Suite or unit number.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_city COMMENT 'City of the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_county COMMENT 'County of the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_state COMMENT 'State or province of the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_zip COMMENT 'Postal code of the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_country COMMENT 'Country of the store.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_gmt_offset COMMENT 'GMT offset for the location.';
ALTER TABLE uw_team_h.retail_channel.store ALTER COLUMN s_tax_precentage COMMENT 'Local tax percentage for the store location.';

COMMENT ON TABLE uw_team_h.retail_channel.time_dim IS 'Time-of-day dimension for hour, shift, and meal-period analysis.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_time_sk COMMENT 'Surrogate key for the time of day.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_time_id COMMENT 'Business identifier for the time of day.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_time COMMENT 'Time of day value.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_hour COMMENT 'Hour component of the time.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_minute COMMENT 'Minute component of the time.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_second COMMENT 'Second component of the time.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_am_pm COMMENT 'AM/PM indicator.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_shift COMMENT 'Shift bucket for the time of day.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_sub_shift COMMENT 'Sub-shift bucket for the time of day.';
ALTER TABLE uw_team_h.retail_channel.time_dim ALTER COLUMN t_meal_time COMMENT 'Meal-period bucket for the time of day.';

COMMENT ON TABLE uw_team_h.retail_channel.web_page IS 'Web page dimension with lifecycle, ownership, and page composition attributes.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_web_page_sk COMMENT 'Surrogate key for the web page.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_web_page_id COMMENT 'Business identifier for the web page.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_rec_start_date COMMENT 'Record effective start date.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_rec_end_date COMMENT 'Record effective end date.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_creation_date_sk COMMENT 'Date surrogate key for when the page was created.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_access_date_sk COMMENT 'Date surrogate key associated with page access.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_autogen_flag COMMENT 'Flag indicating whether the page was auto-generated.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_customer_sk COMMENT 'Surrogate key for the associated customer, if any.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_url COMMENT 'URL of the web page.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_type COMMENT 'Web page type.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_char_count COMMENT 'Number of characters on the page.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_link_count COMMENT 'Number of links on the page.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_image_count COMMENT 'Number of images on the page.';
ALTER TABLE uw_team_h.retail_channel.web_page ALTER COLUMN wp_max_ad_count COMMENT 'Maximum number of ads on the page.';

COMMENT ON TABLE uw_team_h.retail_channel.web_site IS 'Website dimension with business ownership, market, and address attributes.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_site_sk COMMENT 'Surrogate key for the website.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_site_id COMMENT 'Business identifier for the website.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_rec_start_date COMMENT 'Record effective start date.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_rec_end_date COMMENT 'Record effective end date.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_name COMMENT 'Website name.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_open_date_sk COMMENT 'Date surrogate key for when the website launched.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_close_date_sk COMMENT 'Date surrogate key for when the website closed.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_class COMMENT 'Website class or tier.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_manager COMMENT 'Website manager name.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_mkt_id COMMENT 'Market identifier for the website.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_mkt_class COMMENT 'Market classification for the website.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_mkt_desc COMMENT 'Market description.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_market_manager COMMENT 'Manager responsible for the market.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_company_id COMMENT 'Company identifier.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_company_name COMMENT 'Company name.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_street_number COMMENT 'Street number portion of the address.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_street_name COMMENT 'Street name portion of the address.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_street_type COMMENT 'Street type portion of the address.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_suite_number COMMENT 'Suite or unit number.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_city COMMENT 'City of the website office.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_county COMMENT 'County of the website office.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_state COMMENT 'State or province of the website office.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_zip COMMENT 'Postal code of the website office.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_country COMMENT 'Country of the website office.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_gmt_offset COMMENT 'GMT offset for the location.';
ALTER TABLE uw_team_h.retail_channel.web_site ALTER COLUMN web_tax_percentage COMMENT 'Local tax percentage for the website location.';

-- Verification
SELECT table_schema, table_name, column_name, comment
FROM uw_team_h.information_schema.columns
WHERE table_schema = 'retail_channel'
ORDER BY table_name, ordinal_position;