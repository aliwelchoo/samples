with nums as (
select 0 as n, 1 as fib
union all
select 1, 1
union all
select 2, 2)

select 
array(select distinct n from nums),
array(select distinct fib from nums)
