from typing import Dict, List, Union
import unittest
import boto3
import os
from faker import Faker  # <- https://faker.readthedocs.io/en/master/fakerclass.html
from datetime import timedelta, datetime
import dataclasses

# so we won't accidentally come to any AWS account
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"

Faker.seed(0)  # <- determination, baby!
fake = Faker()


def tagify(d: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Converts python dict back into AWS repr of tags
    :param d: dict of tags
    :return: AWS repr of tags
    """
    return [{"Key": k, "Value": v} for k, v in d.items()]


@dataclasses.dataclass  # <- more info https://docs.python.org/3/library/dataclasses.html
class Project:
    name: str
    tags: Dict[str, str] = dataclasses.field(default_factory=dict)
    num_instances: int = 1

    def create_default_tags(self):
        return {
            "Name": self.name,
            "Created": fake.date_this_month().isoformat(),
            "Owner": fake.name(),
            "Ticket": f"Devops-{fake.pyint(0, 6000)}",
        }

    def __hash__(self) -> int:
        return hash(self.name)

    def __post_init__(self):
        # this is dataclass specific post-init method
        self.tags.update(self.create_default_tags())

    def create(self, once=True):
        ec2 = boto3.client("ec2", region_name="eu-west-1", endpoint_url="http://localhost:5000")
        ec2_res = boto3.resource("ec2", region_name="eu-west-1", endpoint_url="http://localhost:5000")
        if once:
            if any(ec2_res.images.filter(Filters=[{"Name": "name", "Values": [f"{self.name}"]}])):
                print(f"already registered image {self.name}, that means instances are created too")
                return

        ami_id = ec2.register_image(Name=self.name, Description=self.name)["ImageId"]

        for _ in range(self.num_instances):
            ec2_res.create_instances(
                ImageId=ami_id,
                MaxCount=1,
                MinCount=1,
                InstanceType="m5.large",
                TagSpecifications=[
                    {
                        "Tags": tagify(self.tags),
                        "ResourceType": "instance",
                    }
                ],
            )


projects = [
    Project("Jenkins"),
    Project("S3 exporter", {"Env": "dev"}, 3),
    Project("Thumbnail compressor", {"Env": "Dev", "Team": "Team Rocket"}, 5),
    Project("Sonarqube", {"Team": "Devops"}, 2),
    Project("Uncategorized", num_instances=5),
]

for proj in projects:
    proj.create()
p = Project("Test", {"Env": "test"}, 3)
p.tags.pop("Owner")
p.create()


class Homework:
    """This is your homework, implement the methods and if tests are green, submit it.
    You can use low-level client or high level client and return list of instance classes if you've used high-level one
    and list of instance' dictionaries in case of low-level client
    """
    ec2_res = boto3.resource("ec2", region_name="eu-west-1", endpoint_url="http://localhost:5000")
    ec2_cli = boto3.client("ec2", region_name="eu-west-1", endpoint_url="http://localhost:5000")

    def find_by_tag(self, tag_name, tag_value):
        """This method should return instances that have `tag_name` == `tag_value`

        Args:
            tag_name ([type]): [description]
            tag_value ([type]): [description]
        """
        filters = [{'Name': 'tag:'+tag_name, 'Values': [tag_value]}]
        response = self.ec2_cli.describe_instances(Filters=filters)
        inst_list = []
        for reservation in (response["Reservations"]):
            for instance in  reservation["Instances"]:
                inst_list.append(instance["InstanceId"])
        # print(f"this is mine: {inst_list}")
        return inst_list
        # filters = [{'Name': "tag:tag_name", 'Values': ["tag_value"]}]


        #     for tag in instance.tags:
        #         if tag['Key'] == tag_name and tag['Value'] == tag_value:
        #             l.append(instance.tags)
        #             print(l)
        # return l
        # for instance in instances:
        #     print(instance)
        # filters = [{'Name': self.tag_name, 'Value':[self.tag_value]}]
        # for instance in self.ec2_res.instances.all():
        #     # print(instance.tags)
        #     for tag in instance.tags:
        #         if tag['Key'] == tag_name and tag['Value'] == tag_value:
        #             print(instance)
                    # print(tag['Value'])
        # filters = [{'Name':tag_name, 'Values':[tag_value]}]
        # for instance in self.ec2_res.describe_instances(Filters=filters):
        #     print(instance.tags)

        pass

    def list_all_owners(self):
        """This method should list all owners of all instances from instance's tag "Owner"
        Caveat: Owner might be listed only once!
        """
        list_owners = []
        for instance in self.ec2_res.instances.all():
            # print(instance.tags)
            for tag in instance.tags:
                if tag['Key'] == 'Owner':
                    list_owners.append(tag['Value'])
        return (set(list_owners))

        # l_owners = []
        # filter = [{'Name': 'tag:Owner'}]
        # for instance in self.ec2_res.instances.filter(Filters=filter):
        #     print(instance.tags)
        #
        #     for tag in instance.tags:
        #         l_owners.append(tag['Value'])
        #         print(l_owners)

        pass

    def list_old_amis(self, threshold_days=30):
        """This method should return all AMI images that are older than `threshold_days` days (use datetime.timedelta and datetime.fromisoformat)
        see https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat
        """
        from datetime import timedelta, datetime

        l = []
        delta2 = datetime.today()

        images = self.ec2_cli.describe_images()['Images']
        for ami in images:
            creation_date = ami['CreationDate']
            ami_id = ami['ImageId']
            delta1 = datetime.fromisoformat(creation_date[:-1])
            # print(delta1)
            # print(delta2)
            if delta2 - delta1 <= timedelta(days=threshold_days):
                l.append(ami_id)
        return l

        pass

    def find_jenkins(self):
        """This method should use boto3 and return instances that have tag "Project" == "Jenkins" """

        instance_ids = []
        response = self.ec2_cli.describe_instances(Filters=[{"Name": "tag:Project", "Values": ["Jenkins"]}])
        instances_full_details = response['Reservations']
        for instance_detail in instances_full_details:
            group_instances = instance_detail['Instances']

            for instance in group_instances:
                instance_id = instance['InstanceId']
                instance_ids.append(instance_id)
        print(f"This is my list: {instance_ids}")
        return instance_ids

        # l = []
        # filters = [{"Name": "tag:Project", "Values": ["Jenkins"]}]
        # jenkins = self.ec2_cli.describe_instances(Filters=filters)
        # for ins_inf in jenkins["Reservations"][0]["Instances"]:
        #     print(ins_inf['InstanceId'])
            # print(f"This is Reservations: {ins_inf=}")
            # for ins_id in ins_inf["Instances"]:
            #     print(f"This is Instances: {ins_id}")
            #     for jenkins_inst in ins_id["InstanceId"]:
            #         print(f"This is ID of jenkins: {jenkins_inst}")
            #         l.append(jenkins_inst)

        # jenkins_machines = self.ec2_res.instances.filter(Filters=[{"Name": "tag:Project", "Values": ["Jenkins"]}])
        # for instance in jenkins_machines:
        #     l.append(instance.instance_id)
        #     print(instance.instance_id)
        #     print(l)
        # return l
        # jenkins_inst = ins_id["InstanceId"]
        # l.append(jenkins_inst)
        # return l
                # print(ins_id["InstanceId"])
        # jenkins_inst = list(jenkins_inst)
        # return ins_id["InstanceId"]
        # jenkins_id = jenkins["Instances"]
        # print(jenkins)
        pass


class Homework6Test(unittest.TestCase):
    def setUp(self) -> None:
        self.ec2_resource = boto3.resource(
            "ec2", region_name="eu-west-1", endpoint_url="http://localhost:5000"
        )
        self.ec2_client = boto3.client("ec2", region_name="eu-west-1", endpoint_url="http://localhost:5000")
        self.hw = Homework()

    def get_object_attr(self, o, attr, alternative_attr, default=None):
        if hasattr(o, attr):
            return getattr(o, attr, default)
        elif isinstance(o, dict):
            iid = o.get(alternative_attr, default)
            self.assertTrue(iid is not None)
            return iid

    def get_instance_id(self, instance) -> str:
        return self.get_object_attr(instance, "id", "InstanceId")

    def get_ami_id(self, image):
        return self.get_object_attr(image, "id", "ImageId")

    def get_owner(self, instance):
        tags = self.get_object_attr(instance, "tags", "Tags")
        self.assertTrue(tags is not None)
        # [{"Key": k, "Value": v} for k, v in d.items()]
        tags = {x.get("Key"): x.get("Value") for x in tags}
        return tags.get("Owner")

    def test_find_jenkins(self):
        truth = self.ec2_resource.instances.filter(Filters=[{"Name": "tag:Project", "Values": ["Jenkins"]}])
        truth = list(map(self.get_instance_id, truth))
        results = self.hw.find_jenkins()
        results = map(self.get_instance_id, results)
        self.assertEqual(sorted(truth), sorted(results))

    def test_find_old_amis(self):
        for threshold in [30, 60]:
            truth = filter(
                lambda x: datetime.fromisoformat(x.creation_date[:-1])
                <= datetime.now() - timedelta(days=threshold),
                self.ec2_resource.images.all(),
            )
            truth = map(self.get_ami_id, truth)
            truth = list(sorted(truth))
            results = map(self.get_ami_id, self.hw.list_old_amis(threshold_days=threshold))
            self.assertEqual(sorted(results), truth)

    def test_list_owners(self):
        truth = self.ec2_resource.instances.filter(Filters=[{"Name": "tag-key", "Values": ["Owner"]}])
        truth = map(self.get_owner, truth)
        results = self.hw.list_all_owners()
        self.assertEqual(sorted(set(truth)), sorted(results))

    def test_find_by_tag(self):
        truth = self.ec2_resource.instances.filter(Filters=[{"Name": "tag:Env", "Values": ["test"]}])
        truth = map(self.get_instance_id, truth)
        results = self.hw.find_by_tag("Env", "test")
        results = map(self.get_instance_id, results)
        self.assertEqual(sorted(truth), sorted(results))


if __name__ == "__main__":
    unittest.main()
