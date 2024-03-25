CREATE PROCEDURE InvokeRESTEndpoint
AS
BEGIN
    DECLARE @QuestionText NVARCHAR(MAX)
    DECLARE @APIEndpoint NVARCHAR(MAX)
    DECLARE @APIKey NVARCHAR(MAX)

    -- Get the question details from the Questions table
    SELECT TOP 1 @QuestionText = QuestionText, @APIEndpoint = APIEndpoint, @APIKey = APIKey
    FROM Questions
    WHERE Answered = 0 -- Assuming you have a column to track if the question has been answered

    -- Invoke the REST API using the question details
    -- You can use the built-in SQL Server functions like sp_OACreate, sp_OAMethod, etc. to make the API call

    -- Update the Questions table to mark the question as answered
    UPDATE Questions
    SET Answered = 1
    WHERE QuestionText = @QuestionText
END