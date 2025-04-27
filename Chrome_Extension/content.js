//Right now works best for greenhouse


//be on current page
//Send question to backend fastapi
//get answer from backend llm
//then answer depending on the question type

//before scanning and sending questions, frontend takes in resume and scans in

//when scanning question, it first sees what type of question it is.
//Based on the type of question, it calls the backend and sends the options list and question type
//The backend llm will then answer the question based on the options list and nlp simlarity matches the llm answer and option,
//then this is sent to the frontend and it filled in directly.
