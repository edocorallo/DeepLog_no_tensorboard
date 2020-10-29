import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import TensorDataset, DataLoader
import argparse
import os

parser = argparse.ArgumentParser()
group=parser.add_mutually_exclusive_group()
group.add_argument("-b","--backend",action="store_true",help="Used if you want to train with storm-backend log type.")
parser.add_argument('-log_file',default='frontend',type=str)
parser.add_argument('-num_layers', default=2, type=int)
parser.add_argument('-hidden_size', default=64, type=int)
parser.add_argument('-window_size', default=10, type=int)
args = parser.parse_args()
if args.backend:
        log_type="backend-server"
else:
        log_type="frontend-server"

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
def num_classes(name):
    uniq=[]
    with open('data/' + name, 'r') as file:
        for line in file:
                line=line.strip().split()
                for char in line:
                        if char!=0 and char not in uniq:
                                uniq.append(char)
    return len(uniq)

def generate(name):
    num_sessions = 0
    inputs = []
    outputs = []
    with open('data/' + name, 'r') as f:
        for line in f.readlines():
            num_sessions += 1
            line = tuple(map(lambda n: n - 1, map(int, line.strip().split())))
            for i in range(len(line) - window_size):
                inputs.append(line[i:i + window_size])
                outputs.append(line[i + window_size])
    print('Number of sessions({}): {}'.format(name, num_sessions))
    print('Number of seqs({}): {}'.format(name, len(inputs)))
    dataset = TensorDataset(torch.tensor(inputs, dtype=torch.float), torch.tensor(outputs))
    return dataset


class Model(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_keys):
        super(Model, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, num_keys)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out


if __name__ == '__main__':
        
    log_file=args.log_file
    # Hyperparameters
    num_classes = num_classes('{}_train'.format(log_file))
    print("num_classes :  ",num_classes)
    num_epochs = 300
    batch_size = 2048
    input_size = 1
    num_layers = args.num_layers
    hidden_size = args.hidden_size
    window_size = args.window_size
    log_file=args.log_file
    model_dir = 'model'
    log = '[{}]Adam_batch_size={}_epoch={}'.format(log_file,str(batch_size), str(num_epochs))

    model = Model(input_size, hidden_size, num_layers, num_classes).to(device)
    seq_dataset = generate('{}_train'.format(log_file))
    dataloader = DataLoader(seq_dataset, batch_size=batch_size, shuffle=True, pin_memory=True)
    writer = SummaryWriter(log_dir='log/' + log)
    #writer=open('writer.txt','w')

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters())

    # Train the model
    start_time = time.time()
    total_step = len(dataloader)
    for epoch in range(num_epochs):  # Loop over the dataset multiple times
        train_loss = 0
        for step, (seq, label) in enumerate(dataloader):
            # Forward pass
            seq = seq.clone().detach().view(-1, window_size, input_size).to(device)
            output = model(seq)
            loss = criterion(output, label.to(device))

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            train_loss += loss.item()
            optimizer.step()
            writer.add_graph(model, seq)
        print('Epoch [{}/{}], train_loss: {:.4f}'.format(epoch + 1, num_epochs, train_loss / total_step))
        writer.add_scalar('train_loss', train_loss / total_step, epoch + 1)
        #print(train_loss / total_step, file=writer)
    elapsed_time = time.time() - start_time
    print('elapsed_time: {:.3f}s'.format(elapsed_time))
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)
    torch.save(model.state_dict(), model_dir + '/' + log + '.pt')
    writer.close()
    print('Finished Training')
