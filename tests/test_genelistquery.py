from unittest import TestCase
from pred.genelistquery import GeneListQuery

QUERY_BASE = """SET search_path TO %s,public;
select
max(common_name) as common_name,
name,
round(max(value), 4) as max_value,
max(chrom) as chrom,
max(strand) as strand,
max(case strand when '+' then txstart else txend end) as gene_start,
json_agg(json_build_object('value', round(value, 4), 'start', start_range, 'end', end_range)) as pred
from gene_prediction
where{}
( common_name in (select gene_name from custom_gene_list where id = %s)
or
name in (select gene_name from custom_gene_list where id = %s)
)
and
model_name = %s
and
case strand when '+' then
(txstart - %s) <= start_range and (txstart + %s) >= start_range
else
(txend - %s) <= end_range and (txend + %s) >= end_range
end
group by name
order by name{}"""

GENE_LIST_FILTER_WITH_LIMIT = QUERY_BASE.format("\ngene_list = %s\nand", "\nlimit %s offset %s")
GENE_LIST_FILTER = QUERY_BASE.format("", "")

COUNT_QUERY = """SET search_path TO %s,public;
select count(*) from (
select
max(common_name) as common_name,
name,
round(max(value), 4) as max_value,
max(chrom) as chrom,
max(strand) as strand,
max(case strand when '+' then txstart else txend end) as gene_start,
json_agg(json_build_object('value', round(value, 4), 'start', start_range, 'end', end_range)) as pred
from gene_prediction
where
( common_name in (select gene_name from custom_gene_list where id = %s)
or
name in (select gene_name from custom_gene_list where id = %s)
)
and
model_name = %s
and
case strand when '+' then
(txstart - %s) <= start_range and (txstart + %s) >= start_range
else
(txend - %s) <= end_range and (txend + %s) >= end_range
end
group by name
order by name
) as foo"""


class TestGeneListQuery(TestCase):
    def test_gene_list_filter_with_limit(self):
        expected_sql = GENE_LIST_FILTER_WITH_LIMIT
        expected_params = ["hg38", "knowngene", 55, 55, "E2F4", "150", "250", "250", "150", "100", "200"]
        query = GeneListQuery(
            schema="hg38",
            custom_list_id=55,
            custom_list_filter='knowngene',
            model_name="E2F4",
            upstream="150",
            downstream="250",
            limit="100",
            offset="200",
        )
        sql, params = query.get_query_and_params()
        self.maxDiff = None
        self.assertEqual(expected_sql, sql)
        self.assertEqual(expected_params, params)

    def test_gene_list_filter(self):
        expected_sql = GENE_LIST_FILTER
        expected_params = ["hg38", 45, 45, "E2F4", "150", "250", "250", "150"]
        query = GeneListQuery(
            schema="hg38",
            custom_list_id=45,
            custom_list_filter='',
            model_name="E2F4",
            upstream="150",
            downstream="250",
        )
        sql, params = query.get_query_and_params()
        self.assertEqual(expected_sql, sql)
        self.assertEqual(expected_params, params)

    def test_gene_list_count(self):
        expected_sql = COUNT_QUERY
        expected_params = ["hg38", 77, 77, "E2F4", "150", "250", "250", "150"]
        query = GeneListQuery(
            schema="hg38",
            custom_list_id=77,
            custom_list_filter='All',
            model_name="E2F4",
            upstream="150",
            downstream="250",
            count=True
        )
        sql, params = query.get_query_and_params()
        self.assertEqual(expected_sql, sql)
        self.assertEqual(expected_params, params)

