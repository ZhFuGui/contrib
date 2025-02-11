
# 21_1
import numpy as np
import mindspore as ms
import mindspore.ops as ops


def focal_loss(labels, logits, alpha, gamma):
    """Compute the focal loss between `logits` and the ground truth `labels`.

    Focal loss = -alpha_t * (1-pt)^gamma * log(pt)
    where pt is the probability of being classified to the true class.
    pt = p (if true class), otherwise pt = 1 - p. p = sigmoid(logit).

    Args:
      labels: A float tensor of size [batch, num_classes].
      logits: A float tensor of size [batch, num_classes].
      alpha: A float tensor of size [batch_size]
        specifying per-example weight for balanced cross entropy.
      gamma: A float scalar modulating loss from hard and easy examples.

    Returns:
      focal_loss: A float32 scalar representing normalized total loss.
    """
    BCLoss = ops.binary_cross_entropy_with_logits(logits = logits, label = labels,reduction = "none")

    if gamma == 0.0:
        modulator = 1.0
    else:
        modulator = ops.exp(-gamma * labels * logits - gamma * ops.log(1 +
            ops.exp(-1.0 * logits)))

    loss = modulator * BCLoss

    weighted_loss = alpha * loss
    focal_loss = ops.sum(weighted_loss)

    focal_loss /= ops.sum(labels)
    return focal_loss



def CB_loss(labels, logits, samples_per_cls, no_of_classes, loss_type, beta, gamma):
    """Compute the Class Balanced Loss between `logits` and the ground truth `labels`.

    Class Balanced Loss: ((1-beta)/(1-beta^n))*Loss(labels, logits)
    where Loss is one of the standard losses used for Neural Networks.

    Args:
      labels: A int tensor of size [batch].
      logits: A float tensor of size [batch, no_of_classes].
      samples_per_cls: A python list of size [no_of_classes].
      no_of_classes: total number of classes. int
      loss_type: string. One of "sigmoid", "focal", "softmax".
      beta: float. Hyperparameter for Class balanced loss.
      gamma: float. Hyperparameter for Focal loss.

    Returns:
      cb_loss: A float tensor representing class balanced loss
    """
    effective_num = 1.0 - np.power(beta, samples_per_cls)
    weights = (1.0 - beta) / np.array(effective_num)
    weights = weights / np.sum(weights) * no_of_classes

    labels_one_hot = ops.one_hot(labels, no_of_classes).float()

    weights = ms.Tensor(weights).float()
    weights = weights.unsqueeze(0)
    weights = weights.repeat(labels_one_hot.shape[0],0) * labels_one_hot
    weights = weights.sum(1)
    weights = weights.unsqueeze(1)
    weights = weights.repeat(no_of_classes,axis=1)

    if loss_type == "focal":
        cb_loss = focal_loss(labels_one_hot, logits, weights, gamma)
    elif loss_type == "sigmoid":
        cb_loss = ops.binary_cross_entropy_with_logits(input = logits,target = labels_one_hot, weights = weights)
    elif loss_type == "softmax":
        pred = logits.softmax(dim = 1)
        cb_loss = ops.binary_cross_entropy(input = pred, target = labels_one_hot, weight = weights)
    return cb_loss



if __name__ == '__main__':
    no_of_classes = 5
    logits = ops.rand(10,no_of_classes).float()
    labels = ops.randint(0,no_of_classes, size = (10,))
    beta = 0.9999
    gamma = 2.0
    samples_per_cls = [2,3,1,2,2]
    loss_type = "focal"
    cb_loss = CB_loss(labels, logits, samples_per_cls, no_of_classes,loss_type, beta, gamma)
    print(cb_loss)