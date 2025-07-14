# Workflow AI Agent

## Overview
The Workflow AI Agent is designed to enhance daily productivity by automating repetitive tasks and providing intelligent assistance to users. This application leverages AI technologies to streamline workflows, improve efficiency, and reduce manual effort in various processes.

## Features
- **Task Automation**: Automates repetitive tasks to save time and reduce errors.
- **Intelligent Assistance**: Provides recommendations and insights based on user interactions.
- **User-Friendly Interface**: Simple and intuitive interface for easy navigation and usage.
- **Integration Capabilities**: Can be integrated with existing tools and platforms to enhance functionality.

## Getting Started

### Prerequisites
- Python 3.x
- Required packages listed in `requirements.txt`

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/workflow-ai-agent.git
   ```
2. Navigate to the project directory:
   ```
   cd workflow-ai-agent
   ```
3. Install conda (if not installed)
   ```
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
   ```
   Now run the installer:
   ```
   bash miniconda.sh -b -p $HOME/miniconda3
   ```
   Initialize conda for your shell:
   ```
   $HOME/miniconda3/bin/conda init bash
   ```
   Now source the conda configuration and verify the installation:
   ```
   source ~/.bashrc && conda --version
   ```
   Clean up the installer file:
   ```
   rm miniconda.sh
   Restart your terminal or run source ~/.bashrc to ensure conda is fully available
   ```

4. Install the required dependencies:
   ```
   conda create -n .condaenv python=3.9 (create a new environment)
   conda activate .condaenv (activate an environment)
   conda install requirements.txt
   conda list (list installed packages)
   
   ```

### Running the Application
To start the application, run the following command:
```
python src/app.py

or 
# Full path with interpriter env
home/user-name/miniconda3/envs/ai-productivity/bin/python /home/{user-name}/project/AI_Produtivity/ai-productivity-workflow-agent/src/app.py
```

## Usage
- Follow the prompts in the application to utilize the AI Agent's features.
- Refer to the documentation in the `docs` directory for detailed user guides and diagrams.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

flowchart TD
    A[User Initiation<br/>Access Microsoft ADFS] --> B[Input Data<br/>User inputs data or selects task]
    B --> C[Data Processing<br/>AI Agent processes input using algorithms/models]
    C --> D[Task Automation<br/>AI Agent performs automated tasks]
    D --> E[Output Generation<br/>Generate reports, summaries, suggestions]
    E --> F[User Review<br/>User reviews AI output]
    F --> G{User Satisfied?}
    G -->|No| H[Feedback Loop<br/>User provides feedback for improvement]
    H --> C
    G -->|Yes| I[End Process<br/>User can initiate new task or exit]
    I --> J{Continue?}
    J -->|Yes| A
    J -->|No| K[Exit Application]
    
    style A fill:#e1f5fe
    style K fill:#ffebee
    style G fill:#fff3e0
    style J fill:#fff3e0
    style H fill:#f3e5f5