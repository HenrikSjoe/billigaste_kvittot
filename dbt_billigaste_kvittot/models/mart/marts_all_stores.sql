with 
    marts_hemkop as (select * from {{ ref('marts_hemkop') }}),
    marts_citygross as (select * from {{ ref('marts_citygross') }}),
    marts_coop as (select * from {{ ref('marts_coop') }}),
    marts_willys as (select * from {{ ref('marts_willys') }})

select * from marts_hemkop
union all
select * from marts_citygross
union all
select * from marts_coop
union all 
select * from marts_willys
order by store, week desc 
