import os

import numpy as np
import pandas as pd

"""
To answer the following questions, make use of datasets: 
    'scheduled_loan_repayments.csv'
    'actual_loan_repayments.csv'
These files are located in the 'data' folder. 

'scheduled_loan_repayments.csv' contains the expected monthly payments for each loan. These values are constant regardless of what is actually paid.
'actual_loan_repayments.csv' contains the actual amount paid to each loan for each month.

All loans have a loan term of 2 years with an annual interest rate of 10%. Repayments are scheduled monthly.
A type 1 default occurs on a loan when any scheduled monthly repayment is not met in full.
A type 2 default occurs on a loan when more than 15% of the expected total payments are unpaid for the year.

Note: Do not round any final answers.

"""


def calculate_df_balances(df_scheduled, df_actual):
    """
    This is a utility function that creates a merged dataframe that will be used in the following questions.
    This function will not be graded, do not make changes to it.

    Args:
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset
        df_actual (DataFrame): Dataframe created from the 'actual_loan_repayments.csv' dataset

    Returns:
        DataFrame: A merged Dataframe with additional calculated columns to help with the following questions.

    """

    df_merged = pd.merge(df_actual, df_scheduled)

    def calculate_balance(group):
        r_monthly = 0.1 / 12
        group = group.sort_values("Month")
        balances = []
        interest_payments = []
        loan_start_balances = []
        for index, row in group.iterrows():
            if balances:
                interest_payment = balances[-1] * r_monthly
                balance_with_interest = balances[-1] + interest_payment
            else:
                interest_payment = row["LoanAmount"] * r_monthly
                balance_with_interest = row["LoanAmount"] + interest_payment
                loan_start_balances.append(row["LoanAmount"])

            new_balance = balance_with_interest - row["ActualRepayment"]
            interest_payments.append(interest_payment)

            new_balance = max(0, new_balance)
            balances.append(new_balance)

        loan_start_balances.extend(balances)
        loan_start_balances.pop()
        group["LoanBalanceStart"] = loan_start_balances
        group["LoanBalanceEnd"] = balances
        group["InterestPayment"] = interest_payments
        return group

    df_balances = (
        df_merged.groupby("LoanID", as_index=False)
        .apply(calculate_balance)
        .reset_index(drop=True)
    )

    df_balances["LoanBalanceEnd"] = df_balances["LoanBalanceEnd"].round(2)
    df_balances["InterestPayment"] = df_balances["InterestPayment"].round(2)
    df_balances["LoanBalanceStart"] = df_balances["LoanBalanceStart"].round(2)

    return df_balances


# Do not edit these directories
root = os.getcwd()

if "Task_2" in root:
    df_scheduled = pd.read_csv("data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("data/actual_loan_repayments.csv")
else:
    df_scheduled = pd.read_csv("Task_2/data/scheduled_loan_repayments.csv")
    df_actual = pd.read_csv("Task_2/data/actual_loan_repayments.csv")

df_balances = calculate_df_balances(df_scheduled, df_actual)


def question_1(df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 1 default definition.

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The percentage of type 1 defaulted loans (ie 50.0 not 0.5)

    """
    # Work on a copy to avoid mutating the input dataframe
    df_loans = df_balances.copy()

    # Identify months where repayment was below the scheduled amount
    df_loans["Type1DefaultFlag"] = (
        df_loans["ActualRepayment"] < df_loans["ScheduledRepayment"]
    )

    # A loan defaults if this occurs in ANY repayment period
    loan_default_flags = (
        df_loans.groupby("LoanID")["Type1DefaultFlag"]
        .any()
    )

    # Convert proportion of defaulted loans to percentage
    default_rate_percent = loan_default_flags.mean() * 100

    return default_rate_percent


def question_2(df_scheduled, df_balances):
    """
    Calculate the percent of loans that defaulted as per the type 2 default definition

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function
        df_scheduled (DataFrame): Dataframe created from the 'scheduled_loan_repayments.csv' dataset

    Returns:
        float: The percentage of type 2 defaulted loans (ie 50.0 not 0.5)

    """
    # Work on a copy to keep original dataframe unchanged
    df_loans = df_balances.copy()

    # Create year indicator from repayment month
    df_loans["Year"] = np.where(df_loans["Month"] <= 12, 1, 2)

    # Aggregate repayments at loan-year level
    yearly_summary = (
        df_loans
        .groupby(["LoanID", "Year"], as_index=False)
        .agg(
            ScheduledTotal=("ScheduledRepayment", "sum"),
            ActualTotal=("ActualRepayment", "sum"),
        )
    )

    # Calculate unpaid amount
    yearly_summary["UnpaidAmount"] = (
        yearly_summary["ScheduledTotal"] - yearly_summary["ActualTotal"]
    ).clip(lower=0)

    # Flag loan-years exceeding the 15% unpaid threshold
    yearly_summary["Type2DefaultFlag"] = (
        yearly_summary["UnpaidAmount"]
        > 0.15 * yearly_summary["ScheduledTotal"]
    )

    # A loan defaults if the condition occurs in any year
    loan_default_flags = (
        yearly_summary.groupby("LoanID")["Type2DefaultFlag"]
        .any()
    )

    default_rate_percent = loan_default_flags.mean() * 100

    return default_rate_percent


def question_3(df_balances):
    """
    Calculate the anualized portfolio CPR (As a %) from the geometric mean SMM.
    SMM is calculated as: (Unscheduled Principal)/(Start of Month Loan Balance)
    SMM_mean is calculated as (∏(1+SMM))^(1/12) - 1
    CPR is calcualted as: 1 - (1- SMM_mean)^12

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The anualized CPR of the loan portfolio as a percent.

    """
    # Work on a copy for safe transformations
    df_portfolio = df_balances.copy()

    # Unscheduled principal represents excess repayment (prepayment)
    df_portfolio["UnscheduledPrincipal"] = (
        df_portfolio["ActualRepayment"]
        - df_portfolio["ScheduledRepayment"]
    ).clip(lower=0)

    # Aggregate to portfolio level by month
    monthly_portfolio = (
        df_portfolio
        .groupby("Month", as_index=False)
        .agg(
            UnscheduledPrincipal=("UnscheduledPrincipal", "sum"),
            LoanBalanceStart=("LoanBalanceStart", "sum"),
        )
        .sort_values("Month")
    )

    # Calculate Single Monthly Mortality (SMM)
    monthly_portfolio["SMM"] = (
        monthly_portfolio["UnscheduledPrincipal"]
        / monthly_portfolio["LoanBalanceStart"]
    ).fillna(0)

    # Geometric mean SMM
    smm_mean = np.prod(1 + monthly_portfolio["SMM"]) ** (1 / 12) - 1

    # Convert to CPR
    cpr = 1 - (1 - smm_mean) ** 12
    cpr_percent = cpr * 100

    return cpr_percent


def question_4(df_balances):
    """
    Calculate the predicted total loss for the second year in the loan term.
    Use the equation: probability_of_default * total_loan_balance * (1 - recovery_rate).
    The probability_of_default value must be taken from either your question_1 or question_2 answer.
    Decide between the two answers based on which default definition you believe to be the more useful metric.
    Assume a recovery rate of 80%

    Args:
        df_balances (DataFrame): Dataframe created from the 'calculate_df_balances()' function

    Returns:
        float: The predicted total loss for the second year in the loan term.

    """
    # The type 2 default definition is used as the probability of default because it
    # captures material repayment shortfalls over a yearly horizon. This makes it a
    # more appropriate measure for estimating expected credit losses than the type 1
    # definition, which can be triggered by a single missed or partial monthly payment.

    # Use type 2 default rate as probability of default
    probability_of_default = question_2(df_scheduled, df_balances) / 100

    # Exposure entering year 2 = month 12 ending loan balances
    year2_exposure = df_balances.loc[
        df_balances["Month"] == 12,
        "LoanBalanceEnd"
    ].sum()

    recovery_rate = 0.80

    total_loss = (
        probability_of_default
        * year2_exposure
        * (1 - recovery_rate)
    )

    return total_loss