"""
The database loan.db consists of 5 tables:
   1. customers - table containing customer data
   2. loans - table containing loan data pertaining to customers
   3. credit - table containing credit and creditscore data pertaining to customers
   4. repayments - table containing loan repayment data pertaining to customers
   5. months - table containing month name and month ID data

You are required to make use of your knowledge in SQL to query the database object (saved as loan.db) and return the requested information.
Simply fill in the vacant space wrapped in triple quotes per question (each function represents a question)

NOTE:
The database will be reset when grading each section. Any changes made to the database in the previous `SQL` section can be ignored.
Each question in this section is isolated unless it is stated that questions are linked.
Remember to clean your data

"""


def question_1():
    """
    Make use of a JOIN to find the `AverageIncome` per `CustomerClass`
    """

    qry = """
    SELECT
        TRIM(c.CustomerClass) AS CustomerClass,
        ROUND(AVG(cu.Income), 2) AS AverageIncome
    FROM credit c
    JOIN customers cu
        ON TRIM(c.CustomerID) = TRIM(cu.CustomerID)
    GROUP BY TRIM(c.CustomerClass)
    ORDER BY
        CASE TRIM(c.CustomerClass)
            WHEN 'A+' THEN 1
            WHEN 'A' THEN 2
            WHEN 'B' THEN 3
            WHEN 'C' THEN 4
            ELSE 5
        END
    """

    return qry


def question_2():
    """
    Make use of a JOIN to return a breakdown of the number of 'RejectedApplications' per 'Province'.
    Ensure consistent use of either the abbreviated or full version of each province, matching the format found in the customer table.
    """

    qry = """
    SELECT
        CASE TRIM(cu.Region)
            WHEN 'WC' THEN 'WesternCape'
            WHEN 'EC' THEN 'EasternCape'
            WHEN 'FS' THEN 'FreeState'
            WHEN 'GT' THEN 'Gauteng'
            WHEN 'KZN' THEN 'KwaZulu-Natal'
            WHEN 'LP' THEN 'Limpopo'
            WHEN 'MP' THEN 'Mpumalanga'
            WHEN 'NC' THEN 'NorthernCape'
            WHEN 'NW' THEN 'NorthWest'
            ELSE TRIM(cu.Region)
        END AS Region,
        COUNT(*) AS RejectedApplications
    FROM loans l
    JOIN customers cu
        ON TRIM(l.CustomerID) = TRIM(cu.CustomerID)
    WHERE UPPER(TRIM(l.ApprovalStatus)) = 'REJECTED'
    GROUP BY
        CASE TRIM(cu.Region)
            WHEN 'WC' THEN 'WesternCape'
            WHEN 'EC' THEN 'EasternCape'
            WHEN 'FS' THEN 'FreeState'
            WHEN 'GT' THEN 'Gauteng'
            WHEN 'KZN' THEN 'KwaZulu-Natal'
            WHEN 'LP' THEN 'Limpopo'
            WHEN 'MP' THEN 'Mpumalanga'
            WHEN 'NC' THEN 'NorthernCape'
            WHEN 'NW' THEN 'NorthWest'
            ELSE TRIM(cu.Region)
        END
    ORDER BY Region
    """

    return qry


def question_3():
    """
    Making use of the `INSERT` function, create a new table called `financing` which will include the following columns:
    `CustomerID`,`Income`,`LoanAmount`,`LoanTerm`,`InterestRate`,`ApprovalStatus` and `CreditScore`

    Do not return the new table, just create it.
    """

    qry = """
        CREATE TABLE financing AS
    SELECT
        TRIM(cu.CustomerID) AS CustomerID,
        cu.Income,
        l.LoanAmount,
        l.LoanTerm,
        l.InterestRate,
        l.ApprovalStatus,
        cr.CreditScore
    FROM customers cu
    JOIN loans l
        ON TRIM(cu.CustomerID) = TRIM(l.CustomerID)
    JOIN credit cr
        ON TRIM(cu.CustomerID) = TRIM(cr.CustomerID)
    """

    return qry


# Question 4 and 5 are linked


def question_4():
    """
    Using a `CROSS JOIN` and the `months` table, create a new table called `timeline` that sumarises Repayments per customer per month.
    Columns should be: `CustomerID`, `MonthName`, `NumberOfRepayments`, `AmountTotal`.
    Repayments should only occur between 6am and 6pm London Time.
    Null values to be filled with 0.

    Hint: there should be 12x CustomerID = 1.
    """

    qry = """
    CREATE TABLE timeline AS
    SELECT
        TRIM(c.CustomerID) AS CustomerID,
        m.MonthName,
        COALESCE(COUNT(r.CustomerID), 0) AS NumberOfRepayments,
        COALESCE(SUM(r.Amount), 0) AS AmountTotal
    FROM customers c
    CROSS JOIN months m
    LEFT JOIN repayments r
        ON TRIM(c.CustomerID) = TRIM(r.CustomerID)
        AND EXTRACT(MONTH FROM r.RepaymentDate) = m.MonthID
        AND EXTRACT(HOUR FROM (r.RepaymentDate AT TIME ZONE r.TimeZone AT TIME ZONE 'Europe/London'))
            BETWEEN 6 AND 17
    GROUP BY
        TRIM(c.CustomerID),
        m.MonthID,
        m.MonthName
    ORDER BY
        TRIM(c.CustomerID),
        m.MonthID
    """

    return qry


def question_5():
    """
    Make use of conditional aggregation to pivot the `timeline` table such that the columns are as follows:
    `CustomerID`, `JanuaryRepayments`, `JanuaryTotal`,...,`DecemberRepayments`, `DecemberTotal`,...etc
    MonthRepayments columns (e.g JanuaryRepayments) should be integers

    Hint: there should be 1x CustomerID = 1
    """

    qry = """
    SELECT
    CustomerID,

    CAST(SUM(CASE WHEN MonthName = 'January' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JanuaryRepayments,
    SUM(CASE WHEN MonthName = 'January' THEN AmountTotal ELSE 0 END) AS JanuaryTotal,

    CAST(SUM(CASE WHEN MonthName = 'February' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS FebruaryRepayments,
    SUM(CASE WHEN MonthName = 'February' THEN AmountTotal ELSE 0 END) AS FebruaryTotal,

    CAST(SUM(CASE WHEN MonthName = 'March' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MarchRepayments,
    SUM(CASE WHEN MonthName = 'March' THEN AmountTotal ELSE 0 END) AS MarchTotal,

    CAST(SUM(CASE WHEN MonthName = 'April' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AprilRepayments,
    SUM(CASE WHEN MonthName = 'April' THEN AmountTotal ELSE 0 END) AS AprilTotal,

    CAST(SUM(CASE WHEN MonthName = 'May' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS MayRepayments,
    SUM(CASE WHEN MonthName = 'May' THEN AmountTotal ELSE 0 END) AS MayTotal,

    CAST(SUM(CASE WHEN MonthName = 'June' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JuneRepayments,
    SUM(CASE WHEN MonthName = 'June' THEN AmountTotal ELSE 0 END) AS JuneTotal,

    CAST(SUM(CASE WHEN MonthName = 'July' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS JulyRepayments,
    SUM(CASE WHEN MonthName = 'July' THEN AmountTotal ELSE 0 END) AS JulyTotal,

    CAST(SUM(CASE WHEN MonthName = 'August' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS AugustRepayments,
    SUM(CASE WHEN MonthName = 'August' THEN AmountTotal ELSE 0 END) AS AugustTotal,

    CAST(SUM(CASE WHEN MonthName = 'September' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS SeptemberRepayments,
    SUM(CASE WHEN MonthName = 'September' THEN AmountTotal ELSE 0 END) AS SeptemberTotal,

    CAST(SUM(CASE WHEN MonthName = 'October' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS OctoberRepayments,
    SUM(CASE WHEN MonthName = 'October' THEN AmountTotal ELSE 0 END) AS OctoberTotal,

    CAST(SUM(CASE WHEN MonthName = 'November' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS NovemberRepayments,
    SUM(CASE WHEN MonthName = 'November' THEN AmountTotal ELSE 0 END) AS NovemberTotal,

    CAST(SUM(CASE WHEN MonthName = 'December' THEN NumberOfRepayments ELSE 0 END) AS INTEGER) AS DecemberRepayments,
    SUM(CASE WHEN MonthName = 'December' THEN AmountTotal ELSE 0 END) AS DecemberTotal

    FROM timeline
    GROUP BY CustomerID
    ORDER BY CAST(CustomerID AS INTEGER)
    """

    return qry


# QUESTION 6 and 7 are linked, Do not be concerned with timezones or repayment times for these question.


def question_6():
    """
    The `customers` table was created by merging two separate tables: one containing data for male customers and the other for female customers.
    Due to an error, the data in the age columns were misaligned in both original tables, resulting in a shift of two places upwards in
    relation to the corresponding CustomerID.

    Create a table called `corrected_customers` with columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`
    Utilize a window function to correct this mistake in the new `CorrectedAge` column.
    Null values can be input manually - i.e. values that overflow should loop to the top of each gender.

    Also return a result set for this table (ie SELECT * FROM corrected_customers)
    """

    qry = """
    CREATE TABLE corrected_customers AS
    WITH base AS (
        SELECT
            CustomerID,
            Age,
            Gender,
            LEAD(Age, 2) OVER (
                PARTITION BY Gender
                ORDER BY CAST(CustomerID AS INTEGER)
            ) AS ShiftedAge,
            ROW_NUMBER() OVER (
                PARTITION BY Gender
                ORDER BY CAST(CustomerID AS INTEGER)
            ) AS rn,
            COUNT(*) OVER (
                PARTITION BY Gender
            ) AS cnt
        FROM customers
    )
    SELECT
        CustomerID,
        Age,
        CASE
            WHEN ShiftedAge IS NOT NULL THEN ShiftedAge
            WHEN Gender = 'Female' AND rn = cnt - 1 THEN 24
            WHEN Gender = 'Female' AND rn = cnt THEN 34
            WHEN Gender = 'Male' AND rn = cnt - 1 THEN 21
            WHEN Gender = 'Male' AND rn = cnt THEN 64
        END AS CorrectedAge,
        Gender
    FROM base;

    SELECT *
    FROM corrected_customers
    ORDER BY CAST(CustomerID AS INTEGER);
    """

    return qry


def question_7():
    """
    Create a column in corrected_customers called 'AgeCategory' that categorizes customers by age.
    Age categories should be as follows:
        - `Teen`: CorrectedAge < 20
        - `Young Adult`: 20 <= CorrectedAge < 30
        - `Adult`: 30 <= CorrectedAge < 60
        - `Pensioner`: CorrectedAge >= 60

    Make use of a windows function to assign a rank to each customer based on the total number of repayments per age group. Add this into a "Rank" column.
    The ranking should not skip numbers in the sequence, even when there are ties, i.e. 1,2,2,2,3,4 not 1,2,2,2,5,6
    Customers with no repayments should be included as 0 in the result.

    Return columns: `CustomerID`, `Age`, `CorrectedAge`, `Gender`, `AgeCategory`, `Rank`
    """

    qry = """
    WITH customer_repayments AS (
        SELECT
            cc.CustomerID,
            cc.Age,
            cc.CorrectedAge,
            cc.Gender,
            CASE
                WHEN cc.CorrectedAge < 20 THEN 'Teen'
                WHEN cc.CorrectedAge < 30 THEN 'Young Adult'
                WHEN cc.CorrectedAge < 60 THEN 'Adult'
                ELSE 'Pensioner'
            END AS AgeCategory,
            COALESCE(COUNT(r.CustomerID), 0) AS TotalRepayments
        FROM corrected_customers cc
        LEFT JOIN repayments r
            ON TRIM(cc.CustomerID) = TRIM(r.CustomerID)
        GROUP BY
            cc.CustomerID,
            cc.Age,
            cc.CorrectedAge,
            cc.Gender
    )
    SELECT
        CustomerID,
        Age,
        CorrectedAge,
        Gender,
        AgeCategory,
        DENSE_RANK() OVER (
            PARTITION BY AgeCategory
            ORDER BY TotalRepayments DESC
        ) AS Rank
    FROM customer_repayments
    ORDER BY CAST(CustomerID AS INTEGER)
    """

    return qry
